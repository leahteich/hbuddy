DESIGN.md
H-Buddy - Leah Teichholtz and Audrey Vanderslice
CS50 Final Project - Fall, 2020

Our project was made using Python, HTML, CSS, and SQLite. We chose to make our project a website rather than an app because we think
people are more likely to use a website, especially in an academic context, and users are quicker to visit a website URL than to
download an app. Further, a website is more accessible to a broad number of devices and browsers. At its most basic, H-Buddy is a
Flask webapp with data stored in two SQLite tables and templated in a series of HTML pages, styled with CSS and taking advantage of
Bootstrap components. We will now dive into how we designed the most important components of our webapp.

Our most complicated design choices were made in regards to how the matching system would work. We settled on having two SQLite
tables — one would store all the user data, and the other would store all the match data. We gave each user a primary key ID as well,
which allowed us to quickly traverse either table to get pertinent information. The matches table is the more dynamic of the
two — every time a person changes their class to something different (i.e. CS50 —> CS51), we SELECT all the other users who also have
that class, which is noted in the users table. We then create a new row for each user who shares that class alongside the user who
just changed their class, calling them “matcher” and “matchee.” Each matcher and matchee has a match status, which can be 0 (“not
seen yet”), 1 (“user matched”), or -1 (“user passed”). When choosing which cards to display, this means that we pick from cards that
are 0 for the person who is logged in. Our design decision added an extra layer of complexity in that the user could be either the
“matcher” or the “matchee” depending on the order in which the class was chosen or assigned, so our code accounts for both
possibilities and acts appropriately. We believe this is the simplest method, because otherwise it would be tedious to track which
users are matchers and matchees, potentially requiring another table or more searching. Importantly, only the matches that share your
class show up on your page. If someone changes their class, all previous attempted matches (i.e. matches where not both users have
chosen 1) are deleted from the database. This saves space and avoids the possibility of anyone showing up on your profile for a
class you are no longer interested in.

Every time someone “matches” a card, a check is performed to see if the other person has also “checked.” If so, an email is sent
using the Flask mail library and the match status for each should be 1. The match time is also recorded, and the class for which the
match is made. When loading the dashboard, we check for any matches by traversing that table, and load them into the page. These
decisions let us easily and dynamically generate cards on the dashboard which show all matches ever made, even if a person switches
their class they can see all previous matches, the time they were made, and contact information. We wanted these cards to be
informative—showing essential contact information —but simple, because emails can easily be buried in inboxes or sent to spam.

Another important aspect of our app was the login verification. Because we did not have time to apply to use the HarvardKey overlay,
we did a simpler but also effective method to check that users are College students. For every attempted registration, we check that
the string following the last instance of “@” is “college.harvard.edu” using string manipulation in the Python route. Future versions
of the app would hopefully integrate HarvardKey so that someone wouldn’t have to remember another password, and to add security
(as someone could impersonate a Harvard email but not actually be a student here).

We used a number of Bootstrap components as a base for the front-end of our website. On our home page is a photo carousel, which
allows us to display our motto and was implemented with the Bootstrap starter code and our own CSS. We were able to combine Bootstrap
elements with templating, for instance, we inserted our own information into a Bootstrap “card” element on the Dashboard and when
finding matches. We did this for consistent styling and the fluid flexibility that Bootstrap provides, ensuring that the app looks
good on all browser sizes and devices.

