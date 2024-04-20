# Fuchs
This extensive web project is built with Django and consists of several apps to provide a diverse range of functionalities, from scraping events to tracking stocks, and even playing a PyGame that has been converted to WebAssembly code.

## Apps

### Safe
A simple app that allows you to store sensitive information using the Python cryptography package. There is also a chat which allows users to send messages and communicate with each other.

### Events
This scraping app is designed to extract events from the popular platforms **Meetup** and **Eventbrite**. It provides a convenient way to aggregate and display events, keeping users informed about upcoming activities. Classes of events can be blacklisted by specifying keywords.

### Scrape
Another app that scrapes websites. You can define keywords that are searched for on **Kleinanzeigen** as well as **Urlaubspiraten**. Should a new item be listed or a new flight become availabe, an email notification is sent.

### Vocabulary
A vocabulary trainer app based on spaced repetition. It also supports Japanese Hiragana and Kanji.

### Quotes
A very simple app to safe quotes. It also contains an email notification service 'quote of the day'.

### Stocks
This app uses Yahoo Finance to track user-specified stocks. If a stock makes a large movement, an email is sent.

### Frog
A simple frogger game where a frog crosses a street and other obstacles (infinite scroll). The game was created in PyGame and is implemented using WebAssembly code.

### Cookbook
An app that lists recipes.

### Cycle
This app loads cycling routes from an AirTable and displays them as a folium map.

### Travel
A travel blog app, loading posts and images from an AirTable.

### Blog
Another blog app.

## License
This project is licensed under the MIT License. Feel free to use, modify, and distribute the code for your own purposes.

Happy coding!
