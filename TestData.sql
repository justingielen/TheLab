/* Coach Accounts */
insert into User (username, email, password) 
    values ('jordanehart','ehart@email.com','UMBCsoccer!!24');
insert into User (username, email, password) 
    values ('garrettdegnon','hoplax@email.net','HOPlax!!40');
insert into User (username, email, password) 
    values ('alexhood','alexhood@email.com','SJUsoccer!!11');
insert into User (username, email, password)
    values ('camspencer','camspencer@email.com','UCONNhoops!!12');

/* Their Profiles */
insert into Profile (first_name, last_name, city, state, birthday, coach)
    values ('Jordan','Ehart','Ellicott City','MD','2000/03/20',True);
insert into profile (first_name, last_name, city, state, birthday, coach)
    values ('Garrett','Degnon','Harwood','MD','1999/04/25',True);
insert into profile (first_name, last_name, city, state, birthday, coach)
    values ('Alex','Hood','Silver Spring','MD','1999/04/30',True);
insert into profile (first_name, last_name, city, state, birthday, coach)
    values ('Cam','Spencer','Davidsonville','MD','2000/06/08',True);

/* Personal Coach Controls */
insert into profileuser(profile_id, username)
    values ('2','jordanehart');
insert into profileuser(profile_id, username)
    values ('3','garrettdegnon');
insert into profileuser(profile_id, username)
    values ('4','alexhood');
insert into profileuser(profile_id, username)
    values ('5','camspencer');

/* Their Applications */
insert into application(profile_id, record, sport, approved, team)
    values ('2','https://umbcretrievers.com/sports/mens-soccer/roster/jordan-ehart/8175','Soccer',True,'UMBC');
insert into application(profile_id, record, sport, approved, team)
    values ('3','https://hopkinssports.com/sports/mens-lacrosse/roster/garrett-degnon/16781','Lacrosse',True,'Johns Hopkins University');
insert into application(profile_id, record, sport, approved, team)
    values ('4','https://sjuhawks.com/sports/mens-soccer/roster/alex-hood/8673','Soccer',True,"St. John's University");
insert into application(profile_id, record, sport, approved, team)
    values ('5','https://uconnhuskies.com/sports/mens-basketball/roster/cam-spencer/13287','Basketball',True,'University of Connecticut');

/* The Resulting Credentials */
insert into sport(sport)
    values ('Lacrosse');
insert into profile_sport(profile_id, sport)
    values ('2','Soccer');
insert into profile_sport(profile_id, sport)
    values ('3','Lacrosse');
insert into profile_sport(profile_id, sport)
    values ('4','Soccer');
insert into profile_sport(profile_id, sport)
    values ('5','Basketball');