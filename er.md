```mermaid
erDiagram
    categories {
        int id [PK]
        varchar(50) name
        varchar(255) icon
        varchar(7) color
        int sort_order
    }

    markers {
        int id [PK]
        int region_id [FK]
        int category_id [FK]
        varchar(200) name
        text description
        decimal(10,2) x_coord
        decimal(10,2) y_coord
        text screenshot
        datetime created_at
        varchar(100) map_name
        int target_region_id
        varchar(100) target_map_name
        decimal(10,2) target_x
        decimal(10,2) target_y
    }

    regions {
        int id [PK]
        varchar(100) name
        text description
        varchar(255) tile_url
        int sort_order
        datetime created_at
    }

    users {
        int id [PK]
        varchar(50) username
        varchar(255) password_hash
        varchar(255) avatar
        int is_admin
        datetime created_at
    }

    markers }o--|| regions : ""
    markers }o--|| categories : ""
```