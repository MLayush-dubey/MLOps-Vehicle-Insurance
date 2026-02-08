import urllib.request 

url = "https://raw.githubusercontent.com/vikashishere/YT-MLops-Proj1/refs/heads/main/notebook/data.csv"
filename = "data.csv"

urllib.request.urlretrieve(url, filename)
print(f"File downloaded: {filename}")