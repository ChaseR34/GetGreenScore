CREATE EXTENSION postgis;

ALTER TABLE dubuque_lat_lon ADD COLUMN geog geography(Point,4326);
UPDATE dubuque_lat_lon SET geog = ST_MakePoint(longitude, latitude)::geography;

ALTER TABLE dubuque_lat_lon ADD COLUMN geom geometry(Point,4326);
UPDATE dubuque_lat_lon SET geom = ST_MakePoint(longitude, latitude)::geometry;

CREATE INDEX dubuque_geom_index ON dubuque_lat_lon  USING GIST ( geom );

drop table if exists dubuque_greenspace_score;
create table dubuque_greenspace_score as
(

    SELECT parcel_number,
    min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
        st_transform( dubuque_shape.geom, 3587))
) as distance,
       CASE when min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
                                 st_transform( dubuque_shape.geom, 3587))) <= 400 then 3
            when min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
                                 st_transform( dubuque_shape.geom, 3587))) > 400 and
                 min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
                                 st_transform( dubuque_shape.geom, 3587))) <= 800 then 2
            when min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
                                 st_transform( dubuque_shape.geom, 3587))) > 800 and
                 min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
                                 st_transform( dubuque_shape.geom, 3587))) < 1200 then 1
            when min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
                                 st_transform( dubuque_shape.geom, 3587))) >= 1200 and
                 min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
                                 st_transform( dubuque_shape.geom, 3587))) < 100000 then 2
            when min(st_distance(st_transform( dubuque_lat_lon.geom, 3587),
                                 st_transform( dubuque_shape.geom, 3587))) >= 100000  then null
           END
           as green_space_score

    FROM dubuque_lat_lon , dubuque_shape
     WHERE (leisure = 'nature_reserve' or leisure = 'park' or
    dubuque_shape.landuse = 'meadow' or dubuque_shape.landuse = 'forest' or ("natural" is not null and "natural" != 'water'))


GROUP BY parcel_number

);

create index dubuque_greenspace_score_indx on dubuque_greenspace_score(parcel_number);