import React, { Component } from "react";
import "@fortawesome/fontawesome-free/js/fontawesome";
import "@fortawesome/fontawesome-free/css/fontawesome.css";
import "@fortawesome/fontawesome-free/js/solid";
import "@fortawesome/fontawesome-free/js/regular";
import "@fortawesome/fontawesome-free/js/brands";
import { Dropdown } from "react-bootstrap";
import FilteredDropdown from "../filtered-dropdown/filteredDropdown";

import "../static/Sidebar.css";
import { CONSTANTS } from "../data/Constants";

export default class Sidebar extends Component {
  constructor(props) {
    super(props);
  }

  handlePageSwitch = (page) => {
    this.props.switchPage(page);
  };

  render() {
    return (
      <div className="left-nav">
        <div className="left-nav-item">
          {/* --- Profile Dropdown --- */}
          <Dropdown onSelect={this.props.onProfileSelect} size="sm">
            <Dropdown.Toggle id="dropdown-profiles">Profiles</Dropdown.Toggle>

            <Dropdown.Menu
              as={FilteredDropdown}
              style={{ maxHeight: 300, overflowY: "auto", overflowX: "hidden" }}
              createNewProfile={this.props.createNewProfile}
            >
              {this.props.profilesList?.map((profile) => {
                let userProfileId =
                  this.props.userProfile[CONSTANTS.PROFILE.ID];
                return (
                  <Dropdown.Item
                    eventKey={profile[CONSTANTS.PROFILE.ID]}
                    key={profile[CONSTANTS.PROFILE.ID]}
                    active={userProfileId == profile[CONSTANTS.PROFILE.ID]}
                  >
                    {profile["profileName"] ?? "Unnamed Profile"}
                  </Dropdown.Item>
                );
              })}
            </Dropdown.Menu>
          </Dropdown>

          {Object.values(CONSTANTS.PAGES).map((page) => {
            if (page.ICON)
              return (
                <div
                  className={`nav-item ${
                    this.props.currentPage === page.NAME ? "active" : ""
                  }`}
                  onClick={() => {
                    this.props.switchPage(page.NAME);
                  }}
                >
                  <i className={`fas ${page.ICON} left-nav-icon`}></i>
                  <span className={`left-nav-label `}>{page.TEXT}</span>
                </div>
              );
          })}

          {/* --- Logout --- */}
          <div className="nav-item" onClick={() => this.props.handleLogout()}>
            <i className="fas fa-sign-out-alt left-nav-icon"></i>
            <span className="left-nav-label">LogOut</span>
          </div>
        </div>
      </div>
    );
  }
}
