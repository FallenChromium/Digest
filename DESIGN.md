# Digest

## Architectural decisions

We're using SQLModel as both a database model and domain model layer, because it results in much less boilerplate code. In case some database conncerns will leak to business logic as a result of this decision, we can create a domain model when necessary. For this to be transparent and easy to refactor, a repository pattern should always be used.
