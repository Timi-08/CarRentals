# Key process algorithms

These algorithms are the shared workflow contracts for the project. Booking
and testimonial data models are not implemented yet; those steps describe the
proposed behavior and should be aligned with their owners before integration.

## Registration

1. If the visitor is already authenticated, redirect to the home page.
2. Validate username, email, password and confirmation; reject an email already
   used by another account.
3. In one database transaction, create the Django User and its one-to-one
   Profile, including the optional phone number.
4. Authenticate the new user, show a success message, and redirect home.
5. If validation fails, show field-level errors and do not create either row.

## Login

1. Present the username/password form and validate credentials with Django's
   authentication backend.
2. Reject invalid credentials without disclosing which value was incorrect.
3. On success, establish the authenticated session and redirect to the
   configured destination (or home).
4. Staff login additionally checks `is_staff` before establishing an admin
   session; non-staff users are rejected.

## Booking (proposed)

1. Require an authenticated user and validate vehicle, start date, end date,
   and `start_date < end_date`.
2. In a transaction, lock/check the vehicle and reject it if it is not
   generally available.
3. Check for an overlapping booking for that vehicle in a blocking status
   (pending or confirmed): existing start is before requested end and existing
   end is after requested start. Reject conflicts.
4. Create a pending booking and calculate the quoted total from the number of
   rental days and current daily price.
5. Show the booking reference and pending status. Recheck conflicts when an
   administrator confirms to handle concurrent requests.

## Admin confirms or cancels a booking (proposed)

1. Require staff authorization and load the booking with its vehicle.
2. For confirmation, revalidate dates and availability/conflicts in a
   transaction. If valid, change `pending` to `confirmed`; otherwise retain
   its current status and report why confirmation failed.
3. For cancellation, change an eligible pending or confirmed booking to
   `cancelled`; do not delete its history.
4. Record the status change and notify the customer using the project's
   configured notification mechanism. Cancelled bookings no longer block dates.

## Testimonials (proposed)

1. Require an authenticated user and validate a non-empty testimonial body.
2. Create the testimonial as unapproved and associate it with the submitting
   user.
3. Staff review the queue; approval makes it eligible for public display,
   while rejection leaves it hidden.
4. Render only approved testimonials on public pages and escape user content
   through normal template rendering.

## Vehicle management

1. Require staff authorization in Django admin.
2. Create a Brand with a unique name, then create a Vehicle with a required
   brand, valid non-negative daily price, positive seat count, fuel type and
   optional image/description.
3. Edit by updating the selected record; validate all model/form constraints
   before saving.
4. Deleting a vehicle removes that catalogue record. A brand with vehicles
   cannot be deleted; reassign or delete its vehicles first.
5. Set `available` to control public listing and `featured` to opt an available
   vehicle into the home-page feature list.
