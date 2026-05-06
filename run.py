from app import create_app
#importing application factory function to be able to define the app instances.

app = create_app() #Builds the flask application and returns it.

if __name__ == '__main__':
    app.run(debug=True)
    #debug mode active and server automatically takes changes.