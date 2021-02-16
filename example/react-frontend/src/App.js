import "./App.css";
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect,
} from "react-router-dom";
import Login from "./components/Login.js";
import TablePage from "./components/TablePage";
import Home from "./components/Home";
import useToken from "./services/useToken";
import Signup from "./components/Signup";
import { api } from "./services/api";

function App() {
  const { token, setToken } = useToken();

  if (!token) {
    return (
      <Router>
        <div className="auth-wrapper">
          <Switch>
            <Route path="/sign-in">
              <Login setToken={setToken} />
            </Route>
            <Route path="/sign-up">
              <Signup />
            </Route>
            <Route path="/">
              <Redirect to="/sign-in" />
            </Route>
          </Switch>
        </div>
      </Router>
    );
  }

  function Logout() {
    api
      .post(
        "/logout",
        {},
        {
          headers: {
            Authorization:
              "Bearer " + JSON.parse(sessionStorage.getItem("token")).token,
          },
        }
      )
      .then((res) => console.log(res))
      .catch((error) => console.log(error));
    setToken("");
    <Redirect to="/" />;
  }

  return (
    <Router>
      <div className="App">
        <nav className="navbar navbar-expand-lg navbar-dark fixed-top">
          <div className="container">
            <div className="collapse navbar-collapse" id="navbarTogglerDemo02">
              <ul className="navbar-nav ml-auto">
                <li className="nav-item">
                  <Link className="nav-link" to={"/sign-up"}>
                    Create new user
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to={"/"}>
                    Home
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to={"/tables"}>
                    Table Views
                  </Link>
                </li>
                <li className="nav-item">
                  <button className="nav-link btn" onClick={Logout}>
                    Logout
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </nav>
        <Switch>
          <Route exact path="/">
            <Home />
          </Route>
          <Route path="/tables">
            <TablePage />
          </Route>
          <Route path="/sign-up">
            <Signup />
          </Route>
          <Route path="/sign-in">
            <Redirect to="/" />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;
