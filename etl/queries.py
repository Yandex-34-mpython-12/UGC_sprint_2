filmworks_query = """
    SELECT
       fw.id,
       fw.title,
       fw.description,
       fw.rating,
       fw.type,
       fw.created_at,
       fw.updated_at,
       COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'person_role', pfw.role,
                   'person_id', p.id,
                   'person_name', p.full_name
               )
           ) FILTER (WHERE p.id is not null),
           '[]'
       ) as persons,
       COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'genre_id', g.id, 
                   'genre_name', g.name
               )
           ), '[]'
       ) as genres
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE fw.updated_at > TIMESTAMP %s
    GROUP BY fw.id
    ORDER BY fw.updated_at
    ;
    """

genres_query = """
    SELECT DISTINCT ON (g.name)
        g.id,
        g.name
    FROM content.genre g
    WHERE g.updated_at > TIMESTAMP %s
"""

persons_query = """
SELECT
    p.id,
    p.full_name,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'id', fw.id,
            'title', fw.title,
            'imdb_rating', fw.rating,
            'role', pfw.role
        )
    ) AS film_works
FROM
    content.person p
LEFT JOIN
    content.person_film_work pfw ON p.id = pfw.person_id
JOIN
    content.film_work fw ON pfw.film_work_id = fw.id
WHERE
    p.updated_at > TIMESTAMP %s
GROUP BY
    p.id
"""