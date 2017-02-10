# Distributed

How to run 

1. Run python EventService.py on IP 10.0.0.1
2. Run any number of publishers using command "python publisher.py <IPaddress of that publisher>"
	It will ask for inputs which are self explanatory when you run the program
3. Run any number of subscribers using the command  "python subscriber.py <IPaddress of that subscriber>"
	It will ask for inputs which are self explanatory when you run the program

The screenshots of the results of the executions are present in my github link
	
All the conditions in the requirement are met 

•	Should work with all these properties including failing publishers
•	Should work with multiple publishers publishing multiple different publications and multiple subscribers all of them distributed over different hosts over different kinds of network topologies that we can create in Mininet (I might supply some topologies)
•	Subscribers may join any time and leave any time
•	Do end-to-end measurements (time between publication and receipt of info; since the clock is the same on all emulated hosts, we do not have the issue of clocks drifting apart from each other).
