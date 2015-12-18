# AutobahnDemo
Demo of using jquery to communicate with autobahn twisted webserver via web sockets and ajax.

To install you will need to:
- Install python
- Install twisted via pip.  If you get an error "Unable to find vcvarsall.bat" then try installing Visual Studio 2008 Express edition.
- Install autobahn via pip.

Pull the contents to a local directory.  In the same directory run the server: python autobahn_demo_server.py

You should now be able to connect on this URL: http://localhost:9000/autobahn_test.html

Clicking the button "Update Client Count" will make an ajax call to the server.

Clicking the button "Send Message" will send the text via websockets to the server, the server will broadcast it back.

Open the same url on another browser window.  You should be able to send messages from one that are reflected in the other.


