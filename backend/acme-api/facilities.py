"""Building, floor, and seat CRUD operations which only admin can touch"""

from psycopg.errors import ForeignKeyViolation, UniqueViolation

from permissions import require_role
from postgres_service import get_connection


def _require_admin(user: dict) -> None:
    """Only Facility Admins can change facility data."""
    require_role(user, "FACILITY_ADMIN")


def _required_text(data: dict, field: str) -> str:
    """Return a required text field or raise a validation error."""
    value = str(data.get(field, "")).strip()

    if not value:
        raise ValueError(f"{field.replace('_', ' ').title()} is required.")

    return value



# BUILDINGS



def list_buildings() -> list:
    """Return all buildings."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, address
            FROM buildings
            ORDER BY name;
            """
        )

        return cursor.fetchall()


def get_building(building_id: int) -> dict:
    """Return one building."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, address
            FROM buildings
            WHERE id = %s;
            """,
            (building_id,),
        )

        building = cursor.fetchone()

    if building is None:
        raise LookupError("Building not found.")

    return building


def create_building(data: dict, user: dict) -> dict:
    """Create a building."""
    _require_admin(user)

    name = _required_text(data, "name")
    address = str(data.get("address", "")).strip() or None

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO buildings (name, address)
                VALUES (%s, %s)
                RETURNING id, name, address;
                """,
                (name, address),
            )

            building = cursor.fetchone()

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError("A building with that name already exists.") from exc

    return building


def update_building(building_id: int, data: dict, user: dict) -> dict:
    """Update a building."""
    _require_admin(user)

    name = _required_text(data, "name")
    address = str(data.get("address", "")).strip() or None

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE buildings
                SET name = %s,
                    address = %s
                WHERE id = %s
                RETURNING id, name, address;
                """,
                (name, address, building_id),
            )

            building = cursor.fetchone()

        if building is None:
            connection.rollback()
            raise LookupError("Building not found.")

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError("A building with that name already exists.") from exc

    return building


def delete_building(building_id: int, user: dict) -> None:
    """Delete a building."""
    _require_admin(user)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM buildings
                WHERE id = %s
                RETURNING id;
                """,
                (building_id,),
            )

            deleted = cursor.fetchone()

        if deleted is None:
            connection.rollback()
            raise LookupError("Building not found.")

        connection.commit()

    except ForeignKeyViolation as exc:
        connection.rollback()
        raise ValueError(
            "Building cannot be deleted while it still has floors."
        ) from exc


# =========================
# FLOORS
# =========================


def list_floors(building_id: int | None = None) -> list:
    """Return floors, optionally filtered by building."""
    connection = get_connection()

    with connection.cursor() as cursor:
        if building_id is None:
            cursor.execute(
                """
                SELECT
                    floors.id,
                    floors.name,
                    floors.building_id,
                    buildings.name AS building_name
                FROM floors
                JOIN buildings ON buildings.id = floors.building_id
                ORDER BY buildings.name, floors.name;
                """
            )
        else:
            cursor.execute(
                """
                SELECT
                    floors.id,
                    floors.name,
                    floors.building_id,
                    buildings.name AS building_name
                FROM floors
                JOIN buildings ON buildings.id = floors.building_id
                WHERE floors.building_id = %s
                ORDER BY floors.name;
                """,
                (building_id,),
            )

        return cursor.fetchall()


def get_floor(floor_id: int) -> dict:
    """Return one floor."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                floors.id,
                floors.name,
                floors.building_id,
                buildings.name AS building_name
            FROM floors
            JOIN buildings ON buildings.id = floors.building_id
            WHERE floors.id = %s;
            """,
            (floor_id,),
        )

        floor = cursor.fetchone()

    if floor is None:
        raise LookupError("Floor not found.")

    return floor


def create_floor(data: dict, user: dict) -> dict:
    """Create a floor inside an existing building."""
    _require_admin(user)

    name = _required_text(data, "name")

    try:
        building_id = int(data.get("building_id"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Valid building ID is required.") from exc

    get_building(building_id)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO floors (building_id, name)
                VALUES (%s, %s)
                RETURNING id, building_id, name;
                """,
                (building_id, name),
            )

            floor = cursor.fetchone()

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError(
            "That floor already exists in this building."
        ) from exc

    return floor


def update_floor(floor_id: int, data: dict, user: dict) -> dict:
    """Update a floor."""
    _require_admin(user)

    name = _required_text(data, "name")

    try:
        building_id = int(data.get("building_id"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Valid building ID is required.") from exc

    get_building(building_id)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE floors
                SET building_id = %s,
                    name = %s
                WHERE id = %s
                RETURNING id, building_id, name;
                """,
                (building_id, name, floor_id),
            )

            floor = cursor.fetchone()

        if floor is None:
            connection.rollback()
            raise LookupError("Floor not found.")

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError(
            "That floor already exists in this building."
        ) from exc

    return floor


def delete_floor(floor_id: int, user: dict) -> None:
    """Delete a floor."""
    _require_admin(user)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM floors
                WHERE id = %s
                RETURNING id;
                """,
                (floor_id,),
            )

            deleted = cursor.fetchone()

        if deleted is None:
            connection.rollback()
            raise LookupError("Floor not found.")

        connection.commit()

    except ForeignKeyViolation as exc:
        connection.rollback()
        raise ValueError(
            "Floor cannot be deleted while it still has seats."
        ) from exc



# SEATS
# 


def list_seats(floor_id: int | None = None) -> list:
    """Return seats, optionally filtered by floor."""
    connection = get_connection()

    with connection.cursor() as cursor:
        if floor_id is None:
            cursor.execute(
                """
                SELECT
                    seats.id,
                    seats.label,
                    seats.floor_id,
                    floors.name AS floor_name,
                    buildings.id AS building_id,
                    buildings.name AS building_name
                FROM seats
                JOIN floors ON floors.id = seats.floor_id
                JOIN buildings ON buildings.id = floors.building_id
                ORDER BY buildings.name, floors.name, seats.label;
                """
            )
        else:
            cursor.execute(
                """
                SELECT
                    seats.id,
                    seats.label,
                    seats.floor_id,
                    floors.name AS floor_name,
                    buildings.id AS building_id,
                    buildings.name AS building_name
                FROM seats
                JOIN floors ON floors.id = seats.floor_id
                JOIN buildings ON buildings.id = floors.building_id
                WHERE seats.floor_id = %s
                ORDER BY seats.label;
                """,
                (floor_id,),
            )

        return cursor.fetchall()


def get_seat(seat_id: int) -> dict:
    """Return one seat with its building and floor."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                seats.id,
                seats.label,
                seats.floor_id,
                floors.name AS floor_name,
                buildings.id AS building_id,
                buildings.name AS building_name
            FROM seats
            JOIN floors ON floors.id = seats.floor_id
            JOIN buildings ON buildings.id = floors.building_id
            WHERE seats.id = %s;
            """,
            (seat_id,),
        )

        seat = cursor.fetchone()

    if seat is None:
        raise LookupError("Seat not found.")

    return seat


def create_seat(data: dict, user: dict) -> dict:
    """Create a seat inside an existing floor."""
    _require_admin(user)

    label = _required_text(data, "label")

    try:
        floor_id = int(data.get("floor_id"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Valid floor ID is required.") from exc

    get_floor(floor_id)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO seats (floor_id, label)
                VALUES (%s, %s)
                RETURNING id, floor_id, label;
                """,
                (floor_id, label),
            )

            seat = cursor.fetchone()

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError(
            "That seat already exists on this floor."
        ) from exc

    return seat


def update_seat(seat_id: int, data: dict, user: dict) -> dict:
    """Update a seat."""
    _require_admin(user)

    label = _required_text(data, "label")

    try:
        floor_id = int(data.get("floor_id"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Valid floor ID is required.") from exc

    get_floor(floor_id)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE seats
                SET floor_id = %s,
                    label = %s
                WHERE id = %s
                RETURNING id, floor_id, label;
                """,
                (floor_id, label, seat_id),
            )

            seat = cursor.fetchone()

        if seat is None:
            connection.rollback()
            raise LookupError("Seat not found.")

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError(
            "That seat already exists on this floor."
        ) from exc

    return seat


def delete_seat(seat_id: int, user: dict) -> None:
    """Delete a seat."""
    _require_admin(user)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM seats
                WHERE id = %s
                RETURNING id;
                """,
                (seat_id,),
            )

            deleted = cursor.fetchone()

        if deleted is None:
            connection.rollback()
            raise LookupError("Seat not found.")

        connection.commit()

    except ForeignKeyViolation as exc:
        connection.rollback()
        raise ValueError(
            "Seat cannot be deleted while incidents are using it."
        ) from exc