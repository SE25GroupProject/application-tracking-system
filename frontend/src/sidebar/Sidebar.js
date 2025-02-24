import React, { Component } from 'react'
import '@fortawesome/fontawesome-free/js/fontawesome'
import '@fortawesome/fontawesome-free/css/fontawesome.css'
import '@fortawesome/fontawesome-free/js/solid'
import '@fortawesome/fontawesome-free/js/regular'
import '@fortawesome/fontawesome-free/js/brands'

import '../static/Sidebar.css'

export default class Sidebar extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activePage: ''
    };
  }

  handlePageSwitch = (page) => {
    this.setState({ activePage: page });
    this.props.switchPage(page);
  };
  
  render() {
    const { activePage } = this.state;
    return (
      <div className="left-nav">
        <div className="left-nav-item">

          {/* --- Search --- */}
          <div
            className={activePage === 'SearchPage' ? 'nav-item active' : 'nav-item'}
            onClick={() => {
              this.props.switchPage('SearchPage');
              this.setState({ activePage: 'SearchPage' });
            }}
          >
            <i
              className={`fas fa-search ${
                activePage === 'SearchPage' ? 'left-nav-icon-active' : 'left-nav-icon'
              }`}
            ></i>
            <span
              className={
                activePage === 'SearchPage'
                  ? 'left-nav-label-active'
                  : 'left-nav-label'
              }
            >
              Search
            </span>
          </div>

          {/* --- Manage --- */}
          <div
            className={activePage === 'ManageResumePage' ? 'nav-item active' : 'nav-item'}
            onClick={() => {
              this.props.switchPage('ManageResumePage');
              this.setState({ activePage: 'ManageResumePage' });
            }}
          >
            <i
              className={`fas fa-folder ${
                activePage === 'ManageResumePage' ? 'left-nav-icon-active' : 'left-nav-icon'
              }`}
            ></i>
            <span
              className={
                activePage === 'ManageResumePage'
                  ? 'left-nav-label-active'
                  : 'left-nav-label'
              }
            >
              Manage
            </span>
          </div>

          {/* --- Matches --- */}
          <div
            className={activePage === 'MatchesPage' ? 'nav-item active' : 'nav-item'}
            onClick={() => {
              this.props.switchPage('MatchesPage');
              this.setState({ activePage: 'MatchesPage' });
            }}
          >
            <i
              className={`fas fa-check-double ${
                activePage === 'MatchesPage' ? 'left-nav-icon-active' : 'left-nav-icon'
              }`}
            ></i>
            <span
              className={
                activePage === 'MatchesPage'
                  ? 'left-nav-label-active'
                  : 'left-nav-label'
              }
            >
              Matches
            </span>
          </div>

          {/* --- Applications --- */}
          <div
            className={activePage === 'ApplicationPage' ? 'nav-item active' : 'nav-item'}
            onClick={() => {
              this.props.switchPage('ApplicationPage');
              this.setState({ activePage: 'ApplicationPage' });
            }}
          >
            <i
              className={`fas fa-file-alt ${
                activePage === 'ApplicationPage' ? 'left-nav-icon-active' : 'left-nav-icon'
              }`}
            ></i>
            <span
              className={
                activePage === 'ApplicationPage'
                  ? 'left-nav-label-active'
                  : 'left-nav-label'
              }
            >
              Applications
            </span>
          </div>

          {/* --- Profile --- */}
          <div
            className={activePage === 'ProfilePage' ? 'nav-item active' : 'nav-item'}
            onClick={() => {
              this.props.switchPage('ProfilePage');
              this.setState({ activePage: 'ProfilePage' });
            }}
          >
            <i
              className={`fas fa-user-alt ${
                activePage === 'ProfilePage' ? 'left-nav-icon-active' : 'left-nav-icon'
              }`}
            ></i>
            <span
              className={
                activePage === 'ProfilePage'
                  ? 'left-nav-label-active'
                  : 'left-nav-label'
              }
            >
              Profile
            </span>
          </div>

          {/* --- Logout --- */}
          <div
            className="nav-item"
            onClick={() => this.props.handleLogout()}
          >
            <i className="fas fa-sign-out-alt left-nav-icon"></i>
            <span className="left-nav-label">LogOut</span>
          </div>

        </div>
      </div>
    )
  }
}
