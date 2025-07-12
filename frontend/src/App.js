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
import GetCounterGraph from './functions/GetCounterGraph';
import GetCoincidenceCount from './functions/GetCoincidenceCount';
import Menu from './functions/Menu';
import StartSignal from './functions/StartSignal';
import GetCounterData from './functions/GetCounterData';
import TimeTaggerStatus from './functions/TimeTaggerStatus';
import GetCountRate from './functions/GetCountRate';

function App() {
  return (
    // <Router>
    //   <div className="App">
    //     {/* Route Configuration */}
    //     <Routes>
    //       <Route path="/" element={<Home />} /> {/* Updated route path to '/' */}
    //       <Route path="/hello" element={<Hello />} />
    //       <Route path="/form" element={<Form />} />
    //       <Route path="/allocateindex" element={<AllocationIndex />} />
    //       <Route path="/view-user-resource" element={<ViewUserResource />} />
    //       <Route path="/view-all-resource" element={<ViewAllResource />} />
    //       <Route path="/add-switch" element={<CreateSwitch />} />
    //       <Route path="/login" element={<UserLogin />} />
    //       <Route path="/signup" element={<UserSignup />} />
    //       <Route path="/test" element={<Test />} />

    //     </Routes>
    //   </div>
    // </Router>

    <Router>
      <Navbar />
      <Routes>

        {/* Unprotected Routes */}
        <Route element={<UnprotectedRoute />}>
          <Route path="/" element={<Home />} />
          <Route path="/signup" element={<UserSignup />} />
          <Route path="/login" element={<UserLogin />} />
        </Route>

        

        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>

          <Route path="/" element={<Home />} /> {/* Updated route path to '/' */}
          <Route path="/hello" element={<Hello />} />
          <Route path="/form" element={<Form />} />
          <Route path="/allocateindex" element={<AllocationIndex />} />
          <Route path="/view-user-resource" element={<ViewUserResource />} />
          <Route path="/view-all-resource" element={<ViewAllResource />} />
          <Route path="/add-switch" element={<CreateSwitch />} />
          <Route path="/test" element={<Test />} />

          <Route path="/menu" element={<Menu />} />
          <Route path="/start-signal" element={<StartSignal />} />
          <Route path="/get-counter-data" element={<GetCounterData />} />
          <Route path="/get-countrate-data" element={<GetCountRate />} />
          <Route path="/status" element={<TimeTaggerStatus />} />
          <Route path="/get-counter-graph" element={<GetCounterGraph />} />
          <Route path="/get-coincidence-count" element={<GetCoincidenceCount />} />
        </Route>

      </Routes>
    </Router >

  );
}

export default App;
