# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 7 - Setting up the DatabasHandler class and its methods

In this post I will go over the creation of the DatabaseHandler class and its methods. This class handles the interactions with the Postgres database running on a separate computer.

### Previously...
To build the databaseHanlder class I started from the previous testing explained in post 5. So let's review what was in that post. In the post I described the tables being used. First there was the athlete table which holds the athlete id, name, weight and ftp.
```
bike_workouts=# SELECT * FROM athletes;
 athlete_id | name  | weight_kg | ftp
------------+-------+-----------+-----
          1 | Scott |        70 | 237
```
Pretty straightforward. In that post I also introduced the workout_templates table which acts as a sort of catalogue for the available workouts which each have their own table with the timestamp and power data.
I made a diagram to ilustrate the relationship.

![workout_templates_tables](https://user-images.githubusercontent.com/102377660/186242705-69db996a-b5a2-4f71-8ac5-ea256d87570e.png)
As you can see, the workout templates table holds the information about each workout. The workouts themselves are represented in separated tables named according to the template_id. Note that in the 'power' column of the workout tables the power value is represented as a fraction of the rider's ftp. 
Also note that the power shouldn't be changing every second as depicted in the diagram since you'd normally want to stay at a certain intensity for a few minutes at a time. 

And that's about as far as the previous post went. Picking up where it left off let's tak about the 'Rides'. 

### Ride tables

Having tables to store the workout templates is great, but I also wanted to store the completed workouts. To make things a bit clearer let's define some terms. 
I used 'Workout' to refer to templates and possible activities and used 'Ride' to refer to coompleted activities. With this in mind I created additional tables that mirror the templates table but to hold the power that the rider actually produced. Check out the diagram below.

![ride_logs table](https://user-images.githubusercontent.com/102377660/186247330-a904b5d9-1c47-451c-a5af-307ce4eeeec3.png)
Just like for the workouts, there is one table holding the information for each ride and other tables holding the rides themselves. In this case, the ride_logs table holds the ride id, the template id, the athlete id and the data of completion. Then separate ride tables hold the power that the rider produced at each timestamp during the ride. 

