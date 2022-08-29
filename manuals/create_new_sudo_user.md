# Create a new user and give him admin rights

Create the new user

    sudo adduser username
  
Give him admin rights by adding him to the sudo group
  
    sudo usermod -aG sudo username

The sudo command in the beginnig can be left out if logged on as root (e.g. when setting up a brand new Ubuntu installation)
