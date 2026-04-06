#use an official python 3.10 image from docker hub
FROM python:3.10-slim-buster 

#set the working directory in the container 
WORKDIR /app 


#copy your application code 
COPY . /app 


#install the dependencies
RUN pip install -r requirements.txt 


#expose the port FastAPI will run on
EXPOSE 5000


#command to run the FastAPI app
CMD ["python3", "app.py", ]
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]