import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './Home';
import Hello from './Hello';
import Form from './Form';
import AllocationIndex from './AllocationIndex';
import Test from './Test';
import ViewUserResource from './ViewUserResource';
import ViewAllResource from './ViewAllResource';
import CreateSwitch from './CreateSwitch';
import UserLogin from './UserLogin';
import UserSignup from './UserSignup';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Route Configuration */}
        <Routes>
          <Route path="/" element={<Home />} /> {/* Updated route path to '/' */}
          <Route path="/hello" element={<Hello />} />
          <Route path="/form" element={<Form />} />
          <Route path="/allocateindex" element={<AllocationIndex />} />
          <Route path="/view-user-resource" element={<ViewUserResource />} />
          <Route path="/view-all-resource" element={<ViewAllResource />} />
          <Route path="/add-switch" element={<CreateSwitch />} />
          <Route path="/login" element={<UserLogin />} />
          <Route path="/signup" element={<UserSignup />} />

          <Route path="/test" element={<Test />} />

        </Routes>
      </div>
    </Router>
  );
}

export default App;
