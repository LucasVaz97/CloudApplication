### Creating a Cloud Multi-Region Rest WebServer
This project will automatically launch a scalable Flask WebServer with a Mongo DataBase.

##### Install boto3
```bash
pip3 install boto3
```
The file `config.py` can be edited to change details about the instances that are going to be launched.

*NOTE:Changing the userData variables might compromise the application.*
##### Launch the application
```bash
python3 LaunchApplication.py
```
*NOTE:After the Scrip is finished, wait for the autoScale instance to have it's status checks: **2/2 checks**.*
##### Testing

To test if the application is running, connect to your EC2 console and get the **DNS name** of your LoadBalancer.

After that, go to (http://**DNS name**:5000/api/v1/users)
on Postman and make a **get** request.  
It should firstly return an empty list. 

To make **posts**, use the JSON format bellow.  
```json
{
            "name": "Lucas",
            "email": "Lucas@hotmail.com",
            "phone": "31415926535",
            "location": "/todo/api/v1.0/tasks/1"
}
```
