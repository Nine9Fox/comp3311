/*
    COMP3311 24T1 Assignment 1
    IMDB Views, SQL Functions, and PlpgSQL Functions
    Student Name: Yixing Xue
    Student ID: <z5517879>
*/

-- Question 1 --

/**
    Write a SQL View, called Q1, that:
    Retrieves the 10 movies with the highest number of votes.
*/
CREATE OR REPLACE VIEW Q1(Title, Year, Votes) AS
    -- TODO: Write your SQL query here
    select primary_title as title, release_year as year, votes 
    from movies 
    where votes is not null 
    order by votes desc
    limit 10
;

-- Question 2 --

/**
    Write a SQL View, called Q2(Name, Title), that:
    Retrieves the names of people who have a year of death recorded in the database
    and are well known for their work in movies released between 2017 and 2019.
*/
CREATE OR REPLACE VIEW Q2(Name, Title) AS
    -- TODO: Write your SQL query here
    select pe.name as name, m.primary_title as title
    from people pe
    join principals p on pe.id = p.person
    join movies m on p.movie = m.id
    where pe.death_year is not null
    and m.release_year between 2017 and 2019
    order by name
;

-- Question 3 --

/**
    Write a SQL View, called Q3(Name, Average), that:
    Retrieves the genres with an average rating not less than 6.5 and with more than 60 released movies.
*/
CREATE OR REPLACE VIEW Q3(Name, Average) AS
    -- TODO: Write your SQL query here
    select g.name as name, round(avg(m.score), 2) as average
    from genres g
    join movies_genres mg on g.id = mg.genre
    join movies m on m.id = mg.movie
    group by g.id
    having round(avg(m.score), 2) >= 6.5
    and count(mg.movie) > 60
;

-- Question 4 --

/**
    Write a SQL View, called Q4(Region, Average), that:
    Retrieves the regions with an average runtime greater than the average runtime of all movies.
*/
CREATE OR REPLACE VIEW Q4(Region, Average) AS
    -- TODO: Write your SQL query here
    select r.region, round(avg(m.runtime)) as average
    from releases r
    join movies m on m.id = r.movie
    where m.runtime is not null
    group by r.region
    having round(avg(m.runtime)) > (select round(avg(runtime)) from movies where runtime is not null)
    order by round(avg(m.runtime)) desc,  r.region asc
;

-- Question 5 --

/**
    Write a SQL Function, called Q5(Pattern TEXT) RETURNS TABLE (Movie TEXT, Length TEXT), that:
    Retrieves the movies whose title matches the given regular expression,
    and displays their runtime in hours and minutes.
*/
CREATE OR REPLACE FUNCTION Q5(Pattern TEXT)
    RETURNS TABLE (Movie TEXT, Length Text)
    AS $$
        -- TODO: Write your SQL query here
        select primary_title as movie, 
        concat(floor(runtime/60), ' ', 'Hours', ' ', runtime%60, ' ', 'Minutes') as length
        from movies
        where primary_title ~ Pattern
        and runtime is not null
        order by primary_title asc;
    $$ LANGUAGE SQL
;

-- Question 6 --

/**
    Write a SQL Function, called Q6(GenreName TEXT) RETURNS TABLE (Year Year, Movies INTEGER), that:
    Retrieves the years with at least 10 movies released in a given genre.
*/
CREATE OR REPLACE FUNCTION Q6(GenreName TEXT)
    RETURNS TABLE (Year Year, Movies INTEGER)
    AS $$
        -- TODO: Write your SQL query here
        select m.release_year as year, count(*) as movies
        from movies m
        join movies_genres mg on m.id = mg.movie
        join genres g on g.id = mg.genre 
        where g.name = GenreName
        and m.release_year is not null
        group by m.release_year
        having count(*) > 10
        order by count(*) desc;
    $$ LANGUAGE SQL
;

-- Question 7 --

/**
    Write a SQL Function, called Q7(MovieName TEXT) RETURNS TABLE (Actor TEXT), that:
    Retrieves the actors who have played multiple different roles within the given movie.
*/
CREATE OR REPLACE FUNCTION Q7(MovieName TEXT)
    RETURNS TABLE (Actor TEXT)
    AS $$
        -- TODO: Write your SQL query here
        select p.name
        from people p
        join roles r on r.person = p.id        
        join movies m on m.id = r.movie
        where m.primary_title = MovieName
        group by p.name
        having count(r.played) > 1
        order by p.name asc;
    $$ LANGUAGE SQL
;

-- Question 8 --

/**
    Write a SQL Function, called Q8(MovieName TEXT) RETURNS TEXT, that:
    Retrieves the number of releases for a given movie.
    If the movie is not found, then an error message should be returned.
*/
CREATE OR REPLACE FUNCTION Q8(MovieName TEXT)
    RETURNS TEXT
    AS $$
        -- TODO: Write your PLpgSQL function here
        DECLARE
            count_release INTEGER;
            if_exist INTEGER;
        BEGIN
            select count(*)
            into count_release
            from releases r
            join movies m on m.id = r.movie
            where m.primary_title = MovieName;

            select count(*)
            into if_exist
            from movies
            where primary_title = MovieName;

            If if_exist = 0
            then 
                return 'Movie' || '"' || MovieName || '"' || 'not found';
            END If;

            If count_release > 0 
            then 
                return 'Release count:' || ' ' ||count_release;
            END If;

            If count_release = 0 
            then 
                return 'No releases found for' || '"' || MovieName || '"';
            END If;          
        END
    $$ LANGUAGE PLpgSQL
;

-- Question 9 --

/**
    Write a SQL Function, called Q9(MovieName TEXT) RETURNS SETOF TEXT, that:
    Retrieves the Cast and Crew of a given movie.
*/
CREATE OR REPLACE FUNCTION Q9(MovieName TEXT)
    RETURNS SETOF TEXT
    AS $$
        -- TODO: Write your PLpgSQL function here    
        BEGIN
            return query
            select * from (
                select concat('"', p.name, '"', ' worked on ', '"', m.primary_title, '"', ' as a ', pro.name)
                from credits c
                join movies m on c.movie = m.id
                join professions pro on c.profession = pro.id
                join people p on c.person = p.id
                where m.primary_title = MovieName

                union all
                select concat('"', p.name, '"', ' played ', '"', r.played, '"', ' in ', '"',m.primary_title,'"')
                from roles r
                join movies m on r.movie = m.id
                join people p on r.person = p.id
                where m.primary_title = MovieName
            ) as results
            order by 1;
        END
    $$ LANGUAGE PLpgSQL
;

-- Question 10 --

/**
    Write a PLpgSQL Function, called Q10(MovieRegion CHAR(4)) RETURNS TABLE (Year INTEGER, Best_Movie TEXT, Movie_Genre Text,Principals TEXT), that:
    Retrieves the list of must-watch movies for a given region, year by year.
*/
CREATE OR REPLACE FUNCTION Q10(MovieRegion CHAR(4))
    RETURNS TABLE (Year INTEGER, Best_Movie TEXT, Movie_Genre Text, Principals TEXT)
    AS $$
        -- TODO: Write your PLpgSQL function here
        BEGIN
            return query
            select m.release_year:: INTEGER as year, m.primary_title as best_movie,
            string_agg(DISTINCT g.name, ', ' order by g.name) as movie_genre,
            string_agg(DISTINCT p.name, ', ' order by p.name) as principals
            from movies m
            join releases r on m.id = r.movie
            join principals pr on m.id = pr.movie
            join people p on pr.person = p.id            
            join movies_genres mg on m.id = mg.movie
            join genres g on mg.genre = g.id
            where r.region = MovieRegion
            and m.score is not null
            group by m.release_year, m.primary_title, m.score
            having  m.score = max(m.score)
            order by m.release_year desc;
        END
    $$ LANGUAGE PLpgSQL
;
