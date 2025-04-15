import "./static/App.css";

import React from "react";
import Sidebar from "./sidebar/Sidebar";
import ApplicationPage from "./application/ApplicationPage";
import SearchPage from "./search/SearchPage";
import LoginPage from "./login/LoginPage";
import ManageResumePage from "./resume/ManageResumePage";
import ProfilePage from "./profile/ProfilePage";
import axios from "axios";
import MatchesPage from "./matches/MatchesPage";
import { CONSTANTS } from "./data/Constants";

export default class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      currentPage: CONSTANTS.PAGES.LOGIN.NAME,
      sidebar: false,
      userProfile: null,
      profilesList: [],
      defaultProfile: 0,
      showLogoutModal: false, // ✅ State to control the custom modal
    };
    this.sidebarHandler = this.sidebarHandler.bind(this);
    this.updateProfile = this.updateProfile.bind(this);
    this.onProfileSelect = this.onProfileSelect.bind(this);
    this.createNewProfile = this.createNewProfile.bind(this);
    this.setDefaultProfile = this.setDefaultProfile.bind(this);
  }

  updateProfile = (body, name = "") => {
    let profileId = this.state.userProfile[CONSTANTS.PROFILE.ID];

    axios
      .post(`http://localhost:5000/updateProfile/${profileId}`, body, {
        headers: {
          userid: localStorage.getItem("userId"),
          Authorization: `Bearer ${localStorage.getItem("userId")}`,
        },
      })
      .then((res) => {
        let profile = { ...this.state.userProfile, ...body };
        this.setState({
          userProfile: profile,
          currentPage: CONSTANTS.PAGES.PROFILE.NAME,
        });

        if (name) {
          const index = this.state.profilesList.findIndex(
            (prof) =>
              prof[CONSTANTS.PROFILE.ID] ===
              this.state.userProfile[CONSTANTS.PROFILE.ID]
          );
          let updatedProfilesList = [...this.state.profilesList]; // important to create a copy, otherwise you'll modify state outside of setState call
          updatedProfilesList[index][CONSTANTS.PROFILE.PROFILE_NAME] = name;
          this.setState({
            profilesList: updatedProfilesList,
          });
        }
      })
      .catch((err) => {
        console.log(err.message);
      });
  };

  createNewProfile = async (name) => {
    axios
      .post(
        "http://localhost:5000/createProfile",
        { [CONSTANTS.PROFILE.PROFILE_NAME]: name },
        {
          headers: {
            userid: localStorage.getItem("userId"),
            Authorization: `Bearer ${localStorage.getItem("userId")}`,
          },
        }
      )
      .then((res) => {
        let newProfile = {
          [CONSTANTS.PROFILE.ID]: res.data[CONSTANTS.PROFILE.ID],
          [CONSTANTS.PROFILE.PROFILE_NAME]: name,
          [CONSTANTS.PROFILE.IS_DEFAULT]: false,
        };
        this.setState({
          profilesList: [...this.state.profilesList, newProfile],
        });
      })
      .catch((err) => {
        console.log(err.message);
      });
  };

  /**
   * Uses the chosen profile id to witch the current profile being viewed.
   * @param {React.ChangeEvent} event
   */
  onProfileSelect = async (event) => {
    const userId = localStorage.getItem("userId");
    await axios
      .get("http://localhost:5000/getProfile/" + event, {
        headers: {
          userid: userId,
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })
      .then((res) => {
        this.setState({
          userProfile: res.data,
        });
      })
      .catch((err) => console.log(err.message));
  };

  /**
   * Make the current profile the default profile.
   */
  setDefaultProfile = async () => {
    const userId = localStorage.getItem("userId");

    // If the current profile is already the default, don't do anything
    let profileId = this.state.userProfile[CONSTANTS.PROFILE.ID];
    if (this.state.defaultProfile === profileId) return;

    // Set Default proile
    await axios
      .post(
        `http://localhost:5000/setDefaultProfile/${profileId}`,
        {},
        {
          headers: {
            userid: userId,
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      )
      .then((res) => {
        this.setState({
          defaultProfile: res.data[CONSTANTS.PROFILE.DEFAULT_PROFILE],
        });
      })
      .catch((err) => console.log(err.message));
  };

  async componentDidMount() {
    if (localStorage.getItem("token")) {
      const userId = localStorage.getItem("userId");
      await axios
        .get("http://localhost:5000/getProfile", {
          headers: {
            userid: userId,
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        })
        .then((res) => {
          this.sidebarHandler(res.data);
        })
        .catch((err) => console.log(err.message));

      await axios
        .get("http://localhost:5000/getProfileList", {
          headers: {
            userid: userId,
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        })
        .then((res) => {
          this.setState({
            profilesList: res.data[CONSTANTS.PROFILE.PROFILE_LIST],
            defaultProfile: res.data[CONSTANTS.PROFILE.DEFAULT_PROFILE],
          });
        })
        .catch((err) => console.log(err.message));
    }
  }

  sidebarHandler = async (user) => {
    const userId = localStorage.getItem("userId");

    await axios
      .get("http://localhost:5000/getProfileList", {
        headers: {
          userid: userId,
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })
      .then((res) => {
        this.setState({
          profilesList: res.data[CONSTANTS.PROFILE.PROFILE_LIST],
          defaultProfile: res.data[CONSTANTS.PROFILE.DEFAULT_PROFILE],
        });
      })
      .then(() => {
        return axios.get("http://localhost:5000/getProfile", {
          headers: {
            userid: userId,
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
      })
      .then((res) => {
        this.setState({
          userProfile: res.data,
          currentPage: CONSTANTS.PAGES.PROFILE.NAME,
          sidebar: true,
        });
      })
      .catch((err) => console.log(err.message));
  };

  // ✅ Show Logout Modal
  handleLogout = () => {
    this.setState({ showLogoutModal: true });
  };

  // ✅ Confirm Logout
  confirmLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    this.setState({
      sidebar: false,
      showLogoutModal: false,
    });
  };

  // ✅ Cancel Logout
  cancelLogout = () => {
    this.setState({ showLogoutModal: false });
  };

  switchPage(pageName) {
    this.setState({
      currentPage: pageName,
    });
  }

  getCurrentPage(pageName) {
    switch (pageName) {
      case CONSTANTS.PAGES.SEARCH.NAME:
        return <SearchPage />;
      case CONSTANTS.PAGES.APPLICATION.NAME:
        return <ApplicationPage />;
      case CONSTANTS.PAGES.LOGIN.NAME:
        return <LoginPage />;
      case CONSTANTS.PAGES.MANAGE_RESUME.NAME:
        return <ManageResumePage />;
      case CONSTANTS.PAGES.MATCHES.NAME:
        return <MatchesPage profile={this.state.userProfile} />;
      default:
        return (
          <ProfilePage
            profile={this.state.userProfile}
            updateProfile={this.updateProfile.bind(this)}
            setDefaultProfile={this.setDefaultProfile}
            isDefault={
              this.state.profilesList.length > 0
                ? this.state.userProfile[CONSTANTS.PROFILE.ID] ===
                  this.state.defaultProfile
                : false
            }
          />
        );
    }
  }

  render() {
    const { showLogoutModal } = this.state;

    return (
      <div>
        {this.state.sidebar ? (
          <div className="main-page">
            <Sidebar
              switchPage={this.switchPage.bind(this)}
              handleLogout={this.handleLogout}
              onProfileSelect={this.onProfileSelect}
              profilesList={this.state.profilesList}
              defaultProfile={this.state.defaultProfile}
              userProfile={this.state.userProfile}
              createNewProfile={this.createNewProfile}
              currentPage={this.state.currentPage}
            />
            <div className="main">
              <div className="container">
                <h1
                  className="text-center"
                  style={{ marginTop: "2%", fontWeight: "300" }}
                >
                  Application Tracking System
                </h1>
                {this.getCurrentPage(this.state.currentPage)}
              </div>
            </div>
          </div>
        ) : (
          <div className="main">
            <div className="content">
              <h1
                className="text-center"
                style={{
                  marginTop: 30,
                  padding: "0.4em",
                  fontWeight: "300",
                }}
              >
                Application Tracking System
              </h1>
              <LoginPage side={this.sidebarHandler} />
            </div>
          </div>
        )}

        {/* ✅ Custom Logout Modal */}
        {showLogoutModal && (
          <div className="modal-overlay">
            <div className="custom-modal">
              <h2>Confirm Logout</h2>
              <p>Are you sure you want to logout?</p>
              <div className="modal-buttons">
                <button className="btn cancel-btn" onClick={this.cancelLogout}>
                  Cancel
                </button>
                <button className="btn logout-btn" onClick={this.confirmLogout}>
                  Logout
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ✅ Modal Styling */}
        <style>{`
					.modal-overlay {
						position: fixed;
						top: 0;
						left: 0;
						width: 100%;
						height: 100%;
						background: rgba(0, 0, 0, 0.5);
						display: flex;
						align-items: center;
						justify-content: center;
						z-index: 999;
					}

					.custom-modal {
						background: #fff;
						padding: 20px 30px;
						border-radius: 8px;
						box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
						text-align: center;
						width: 300px;
					}

					.custom-modal h2 {
						margin-bottom: 10px;
					}

					.modal-buttons {
						margin-top: 20px;
						display: flex;
						justify-content: space-between;
					}

					.btn {
						padding: 10px 20px;
						border: none;
						border-radius: 4px;
						cursor: pointer;
						color: #fff;
					}

					.cancel-btn {
						background-color: #3498db;
					}

					.logout-btn {
						background-color: #e74c3c;
					}

					.btn:hover {
						opacity: 0.9;
					}
				`}</style>
      </div>
    );
  }
}
