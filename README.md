# INFO3180-Group-FinalProject

A DATING APPLICATION web platform (called DriftDater) that allows registered users to create detailed profiles, discover compatible matches, and initiate connections with other users. The application will be built using Vue 3 frontend framework and Flask backend API, with a database to store user profiles and matching information.


## Authors

- [@DannyB67](https://github.com/DannyB67)
- [@ruthbak](https://github.com/ruthbak)
- [@sukanayna_hoo](https://github.com/sukanayna_hoo)


## Tech Stack

- API Framework (Backend): ✓ Flask (Python) ✓ RESTful API design with proper HTTP methods 
✓ Database schema with minimum 4-5 normalized tables 
✓ Authentication using sessions 
✓ Input validation and error handling 
✓ CORS configuration for frontend communication 
✓ Database migrations (using Flask-Migrate)
- Authentication: JWT
- Database:✓ SQLAlchemy ORM models 
✓ Proper relationships (one-to-many, many-to-many) 
✓ Indexes on frequently queried columns 
✓ Data integrity constraints 
- Frontend (Vue): ✓ Component-based architecture with reusable components 
✓ State management (Vuex or Pinia recommended) 
✓ Routing (Vue Router for page navigation) 
✓ Responsive design (mobile-friendly) 
✓ Form validation and user feedback 
✓ Loading states and error handling 



## Roles
- Project Manager [@sukanayna_hoo](https://github.com/sukanayna_hoo)(Oversees timeline, coordinates team efforts) 
- Backend Lead: [@DannyB67](https://github.com/DannyB67) (Manages API, database, security) 
- Frontend Lead (Manages UI/UX, Vue 3 components) 
- QA/Testing Lead: [@DannyB67](https://github.com/DannyB67) & [@sukanayna_hoo](https://github.com/sukanayna_hoo) (Manages testing, validation, documentation) 
- Deployment Lead (Manages deployments, configurations)
## Features

1. USER AUTHENTICATION & PROFILE MANAGEMENT 
- User registration with email validation 
- Secure login/logout functionality 
- Password hashing (bcrypt or similar) 
- User profile creation and editing 
- Profile fields must include: 
- Basic info (name, age, bio/description) 
- Location/geographic preferences 
- Interests/hobbies (minimum 3) 
- Profile picture upload capability 
- Additional custom fields (minimum 2) 
- Profile visibility controls (public/private) 
2. MATCHING SYSTEM 
- Simple matching algorithm based on: 
- Location proximity (within specified radius) 
- Age range preferences 
- Shared interests 
- At least one additional matching criterion 
- Display matched profiles to logged-in users 
- Like/Dislike/Pass functionality 
- Match notifications and confirmations 
- Mutual match detection (both users like each other) 
- Browse mode with filtering options 
3. USER CONNECTIONS & MESSAGING 
- Simple messaging system for matched users 
- Display conversation list 
- Send and receive messages 
- Message persistence (stored in database) 
- Real-time or near-real-time message updates (Vue reactivity) 
- View message history 
4. SEARCH & DISCOVERY 
- Search functionality by: 
- Location 
- Age range 
- Interests 
- Additional criteria 
- Filter applied matches 
- Sort options (newest, most similar, etc.) 
- Save favorite/bookmarked profiles 
