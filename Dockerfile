#User python 3.11 base image
FROM python:3.11-slim

####Working Directory
WORKDIR /app

####COPY REQUiMENT AND INSTALL ALL DEPENDEICES
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


##Copy
COPY . .

##EXPOSE THE APPLICATION PORT
EXPOSE 8000

#COMMAND TO START FASTAPI APPLICATION
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]





# # /////Docker command here
# docker build -t your_image name .

# docker login

### docker tag image_name username/image_name:latest

##docker push asminpoudel88/image_name:latest



# //docker pull command
# docker pull asminpoudel/bankapi:latest


# docker rmi asminpoudel88/bankapi:latest


# docker run --rm -p 1000:8000 asminpoudel88/bankapi:latest
