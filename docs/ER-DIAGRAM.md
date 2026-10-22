# Car-rental system E-R diagram

This is the proposed shared model contract to circulate before the booking and
testimonial models are implemented. `Profile`, `Brand`, `Vehicle`, `Contact`,
`Subscriber`, and `SiteContent` are supported by the current apps. Booking and
testimonial relationships are proposals for agreement with Person 1; confirm
their foreign-key names and deletion rules with that module's owner before
creating migrations that depend on them.

```mermaid
erDiagram
    USER ||--o| PROFILE : has
    BRAND ||--o{ VEHICLE : manufactures
    USER o|--o{ CONTACT : submits
    USER ||--o{ BOOKING : places
    VEHICLE ||--o{ BOOKING : reserved_for
    USER ||--o{ TESTIMONIAL : writes

    USER {
        integer id PK
        string username UK
        string email
    }
    PROFILE {
        integer id PK
        integer user_id FK,UK
        string phone
        string address
    }
    BRAND {
        integer id PK
        string name UK
    }
    VEHICLE {
        integer id PK
        integer brand_id FK
        string name
        decimal price_per_day
        integer seats
        string fuel_type
        string image
        boolean available
        boolean featured
        text description
    }
    BOOKING {
        integer id PK
        integer user_id FK
        integer vehicle_id FK
        date start_date
        date end_date
        string status
    }
    CONTACT {
        integer id PK
        integer user_id FK, nullable
        string name
        string email
        string subject
        text message
        string status
        datetime created_at
    }
    SUBSCRIBER {
        integer id PK
        string email UK
        datetime subscribed_at
        boolean is_active
    }
    TESTIMONIAL {
        integer id PK
        integer user_id FK
        text message
        boolean is_approved
        datetime created_at
    }
    SITE_CONTENT {
        integer id PK
        string homepage_title
        text homepage_intro
        string contact_email
        string contact_phone
        string contact_address
    }
```

`SiteContent` is intended to have one administrator-managed row. A contact
message can be submitted by a guest (no `user_id`) or tied to an authenticated
user. Subscribers are independent of accounts and are identified by unique
email addresses. Vehicles belong to exactly one brand; deleting a brand with
vehicles should be prevented. A vehicle's `available` flag controls whether it
is offered for rental; booking-date conflicts are a separate concern of the
booking workflow.

# Key definitions

| Entity | Primary key | Important uniqueness / relationship |
| --- | --- | --- |
| User | `id` (Django auth) | `username` unique |
| Profile | `id` | `user_id` unique, one-to-one with User |
| Brand | `id` | `name` unique |
| Vehicle | `id` | `brand_id` references Brand |
| Booking (proposed) | `id` | references User and Vehicle |
| Contact | `id` | optional `user_id` references User |
| Subscriber | `id` | `email` unique |
| Testimonial (proposed) | `id` | references User |
| SiteContent | `id` | singleton row managed by site admin |
