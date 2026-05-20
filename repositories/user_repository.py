from ..config import database
import aiomysql
import math

def calculate_total_pages(total_items: int, per_page: int) -> int:
    """
    Calculate total pagination pages.

    Cases handled:
    1. per_page > total_items
    2. total_items == 0
    """

    if per_page <= 0:
        raise ValueError("per_page must be greater than 0")

    if total_items == 0:
        return 0

    return math.ceil(total_items / per_page)

async def get_user_by_email(email):
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            allowed_columns = ["f_name", "l_name", "email", "role"]

            query = "SELECT * FROM users where email=%s"

            await cursor.execute(query,(email,))

            user = await cursor.fetchone()

            return user

async def create_user(data: dict):
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = "INSERT INTO users (f_name, l_name, email, password, role) VALUES(%s, %s, %s, %s, %s)"
            await cursor.execute(query, (data.f_name, data.l_name, data.email, data.password, data.role.value, ))
            await conn.commit()
            return cursor.lastrowid

async def update_user(user_id,data):
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = "UPDATE users set f_name=%s, l_name=%s, email=%s, role=%s WHERE user_id=%s"
            await cursor.execute(query, (data.f_name, data.l_name, data.email, data.role.value, user_id))
            await conn.commit()
            
            query = "SELECT * FROM users where user_id = %s"

            await cursor.execute(query, (user_id,))

            result = await cursor.fetchone()

            return result

async def get_all_users(request):
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            allowed_columns = ["f_name", "l_name", "email", "role"]

            where = ""
            values = []

            limit = int(request.get("limit", 10))
            offset = int(request.get("offset", 0))

            if "searchColumns" in request and len(request["searchColumns"]) != 0:

                search_columns = [col for col in request["searchColumns"] if col in allowed_columns]

                if len(search_columns) !=0:

                    where_clause = " OR ".join(
                        [f"{col} LIKE %s" for col in search_columns]
                    )

                    where = f"WHERE ({where_clause}) AND is_deleted= %s"

                    if "searchValue" in request:
                        values.extend(
                            [f"%{request['searchValue']}%"] * len(search_columns)
                        )
                    else:
                        values.extend([f"%%"] * len(search_columns))
                    values.extend([0])
            else:
                where = "WHERE is_deleted=%s"
                values.extend([0])

            allowed_orders = ["ASC", "DESC"]
            sort_by = "updated_at" 
            order = allowed_orders[1]

            if request.get("sortByColumn") in allowed_columns:
                sort_by = request["sortByColumn"]

            if request.get("order", "").upper() in allowed_orders:
                order = request["order"].upper()

            FORM = f""" 
                FROM users
                {where}
                ORDER BY {sort_by} {order}
                """

            ## Count total items for pagination
            countSql = f"""
                SELECT COUNT(*) as count
                {FORM}
                """;

            await cursor.execute(countSql, tuple(values))
            total_items = (await cursor.fetchone())["count"]

            if total_items == 0:
                return {
                    "totalItems": 0,
                    "totalPages": 0,
                    "page": 0,
                    "records": []
                }

            sql = f"""
                SELECT *
                {FORM}
                LIMIT %s OFFSET %s
                """
           
            values.extend([limit,offset])

            await cursor.execute(sql, tuple(values))
            
            users = await cursor.fetchall()

            for user in users:
                user['created_at'] = user["created_at"].isoformat()
                user['updated_at'] = user["updated_at"].isoformat()
                del user["password"]
            
            return {
                "totalItems": total_items,
                "totalPages":calculate_total_pages(total_items,limit),
                "page": (offset // limit) + 1,
                "records":users
            } 

async def get_user_by_id(user_id):
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = "SELECT f_name, l_name, email, role FROM users where user_id=%s"

            await cursor.execute(query,(user_id,))

            user = await cursor.fetchone()

            return user

async def delete_user(user_id):
    async with database.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as curosr:
            query = "UPDATE users set is_deleted=1 WHERE user_id=%s"

            await curosr.execute(query, (user_id, ))
            await conn.commit()

            return curosr.rowcount