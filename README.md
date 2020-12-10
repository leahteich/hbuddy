README.md
H-Buddy - Leah Teichholtz and Audrey Vanderslice
CS50 Final Project - Fall, 2020

Video URL: https://www.youtube.com/watch?v=d8YMOK53jLs

The first place to start is to make sure you’re in the same file as the code entitled “application.py” in the directory.
Then, in the terminal window, type “flask run” and enter. Click on the link that appears. Once you’ve arrived at the website,
the first thing to do is register for an account with a Harvard College email. Fill in all the requested boxes and make sure
your passwords match. If you click on “Create Profile” and an error message appears, read the error (i.e. “passwords do not
match,” “sign up with your Harvard email,” etc.) and amend your response accordingly.

After you have registered, you will arrive at your dashboard. Start by clicking on the button that says Welcome in the crimson
navigation bar at the top. There you will find an overview of H-Buddy’s mission as well as our motto “Connect. Create. Ace.”
After reading, click on the navigation bar button that says “Dashboard.” You will not be able to find buddies until you fill in a
class, which makes sense — you wouldn’t want to sort through lots of users in classes unrelated to yours. Next, you can click on the
button that says “Update my Profile” and fill in all of the requested information and your class. None of this information is
technically required (besides class, so you can find Buddies), but we anticipate users wanting to fill in as much as they can so that
others get the full picture. H-Buddy still has a limited number of registered profiles, but you can test our program by making your
class “CS50,” “CS51,” or “MATH55” because those are the classes for which we’ve registered users (CS51 has the most registered users,
so we suggest using that class to start. Please note that there are a few profiles named Audrey that are in different classes that we
created for testing). You can also make multiple logins or make your friends login so that you can see the different cards that are
generated.

Once you’ve clicked “Update Profile,” you will arrive back at the dashboard. Click on the button that says “Find buddies in [class
entered in profile]” to start looking for PSET partners! You will see different cards with various profiles and either click on the
green check mark to match them or the red cross to “pass” on them. You will only be able to see profiles of people in the class you
entered in your profile. On each card, you will see their work preferences, time zone, length of commitment, location, and bio. Go
through as many profiles as you’d like, matching or passing based on what profile factors you care about most. Note that if you try
to search for buddies in a class that no other H-Buddy user is looking for a partner in, no potential matches will appear and a
message will appear saying so. If you change your class, a new set of potential Buddies will appear, even if you haven’t fully gone
through the Buddies from the original class.

If you and another user both match one another, their card will appear at the bottom of your dashboard. In case you’re not online,
both of you will also receive an email on your Harvard email accounts that includes all necessary contact information for you to begin
collaborating (You may need to recruit a Harvard friend to test out this feature! Alternatively, we will check the account labeled
Audrey Vanderslice (in CS51) frequently so that we can match you back).

Occasionally, if the website has been left idling too long, Internal Server Errors might appear out of nowhere. If this happens, go
back to your IDE, and enter “flask run” again. In addition, emails will sometimes go to the junk folder, but after marking the first
as not spam, subsequent emails should not have that issue.

