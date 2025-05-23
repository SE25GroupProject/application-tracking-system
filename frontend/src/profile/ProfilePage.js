import React, { useEffect, useState } from "react";
import LocationModal from "./CustomModal";
import SkillsModal from "./CustomModal";
import ExperienceLevelModal from "./CustomModal";
import JobModeModal from "./CustomModal";
import ProfileModal from "./CustomProfileModal";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { CONSTANTS } from "../data/Constants";
import {
  faCheck,
  faClose,
  faEdit,
  faEnvelope,
  faLocationDot,
  faPenToSquare,
  faPhone,
  faStar,
} from "@fortawesome/free-solid-svg-icons";

import { faStar as farStar } from "@fortawesome/free-regular-svg-icons";
import { Button, Col, Form, Row } from "react-bootstrap";

const ProfilePage = (props) => {
  const [locationModalOpen, setLocationModalOpen] = useState(false);
  const [skillsModalOpen, setSkillsModalOpen] = useState(false);
  const [ExpLevelModalOpen, setExpLevelModalOpen] = useState(false);
  const [profileModalOpen, setProfileModalOpen] = useState(false);
  const [jobModeModalOpen, setJobModeModalOpen] = useState(false);

  const profile = props.profile;
  const [profileName, setProfileName] = useState(
    profile[CONSTANTS.PROFILE.PROFILE_NAME] ?? "Default Profile"
  );
  const [editingProfileName, setEditingProfileName] = useState(false);

  useEffect(() => {
    setProfileName(props.profile[CONSTANTS.PROFILE.PROFILE_NAME]);
  }, [props.profile]);

  const onProfileNameChange = (event) => {
    setProfileName(event.target.value);
  };

  const updateProfileName = () => {
    props.updateProfile(
      { [CONSTANTS.PROFILE.PROFILE_NAME]: profileName },
      profileName
    );
  };

  /**
   * Given a full name string, the method returns initials or the abbreviated name of the user profile in terms of initial letters of the first and last word of the full name
   * @param {String} fullName This string is the full name of the user
   * @returns The abbreviated name string
   */
  function getUserInitials(fullName) {
    if (fullName && fullName.trim().length > 0) {
      const arr = fullName.trim().split(" ");
      let initials = arr[0].substring(0, 1);
      if (arr.length > 1) {
        initials += arr[arr.length - 1].substring(0, 1);
      }
      return (
        <span style={{ fontSize: 60, letterSpacing: 1.2 }}>{initials}</span>
      );
    }
    return (
      <span style={{ fontSize: 60, letterSpacing: 1.2 }}>
        <FontAwesomeIcon icon="fa-solid fa-user" style={{ color: "#fbfcfe" }} />
      </span>
    );
  }

  function setNewDefaultProfile() {
    props.setDefaultProfile();
  }

  return (
    <div
      className="container"
      style={{ marginTop: "2.5rem" }}
      data-testid="profile-page"
    >
      <Row style={{ alignItems: "center" }}>
        <Col xs="auto" className="my-auto">
          <h3 className="my-0">Profile: </h3>
        </Col>

        <Col xs="auto" className="my-auto">
          <Form.Control
            plaintext={!editingProfileName}
            readOnly={!editingProfileName}
            value={profileName}
            onChange={onProfileNameChange}
            id="profileName"
          />
        </Col>

        <Col xs="auto">
          <Button
            onClick={() => {
              setProfileName(
                profile[CONSTANTS.PROFILE.PROFILE_NAME] ?? "Default Profile"
              );
              setEditingProfileName(!editingProfileName);
            }}
          >
            {editingProfileName ? (
              <FontAwesomeIcon icon={faClose} />
            ) : (
              <FontAwesomeIcon icon={faEdit} />
            )}
          </Button>
        </Col>
        <Col xs="auto">
          {editingProfileName && (
            <Button
              onClick={() => {
                updateProfileName();
                setEditingProfileName(!editingProfileName);
              }}
            >
              <FontAwesomeIcon icon={faCheck} />
            </Button>
          )}
        </Col>
        <Col>
          {props.isDefault ? (
            <Button variant="link" className="default-btn">
              <FontAwesomeIcon icon={faStar} title="Filled Star" />
            </Button>
          ) : (
            <Button
              variant="link"
              className="default-btn"
              onClick={setNewDefaultProfile}
            >
              <FontAwesomeIcon icon={farStar} title="Empty Star" />
            </Button>
          )}
        </Col>
      </Row>
      <div className="row ---gx-5">
        <div className="col-sm-12 col-lg-4 my-3">
          <div
            className="card p-4"
            style={{
              boxShadow: "0px 5px 12px 0px rgba(0,0,0,0.1)",
            }}
          >
            <FontAwesomeIcon
              icon={faPenToSquare}
              size="1x"
              onClick={() => setProfileModalOpen(true)}
              cursor="pointer"
              style={{ position: "absolute", top: "15", right: "15" }}
            />
            <div className="text-center my-3">
              <div
                className="text-center mt-3 d-inline-flex justify-content-center align-items-center"
                style={{
                  width: "10rem",
                  maxWidth: "100%",
                  aspectRatio: "1",
                  borderRadius: "100%",
                  backgroundColor: "#296E85",
                  color: "#fff",
                  boxShadow: "0px 5px 12px 10px rgba(0,0,0,0.1)",
                }}
              >
                {getUserInitials(profile.fullName)}
              </div>
            </div>
            <div className="text-center mt-3">
              <h3 className="card-title mb-1">
                {profile[CONSTANTS.PROFILE.NAME]
                  ? profile[CONSTANTS.PROFILE.NAME]
                  : ""}
              </h3>
              <span style={{ fontSize: 20 }}>
                {profile[CONSTANTS.PROFILE.UNIVERSITY]
                  ? profile[CONSTANTS.PROFILE.UNIVERSITY]
                  : ""}
              </span>
            </div>
            <hr className="my-4" />
            <div className="row gy-4">
              <div className="col-12 d-flex align-items-center">
                <FontAwesomeIcon icon={faEnvelope} size="1x" />
                <span className="mx-2 profile-detail">
                  {profile[CONSTANTS.PROFILE.EMAIL]
                    ? profile[CONSTANTS.PROFILE.EMAIL]
                    : ""}
                </span>
              </div>
              <div className="col-12 d-flex align-items-center">
                <FontAwesomeIcon icon={faPhone} size="1x" />
                <span className="mx-2 profile-detail">
                  {profile[CONSTANTS.PROFILE.CONTACT]
                    ? profile[CONSTANTS.PROFILE.CONTACT]
                    : ""}
                </span>
              </div>
              <div className="col-12 d-flex align-items-center">
                <FontAwesomeIcon icon={faLocationDot} size="1x" />
                <span className="mx-2 profile-detail">
                  {profile[CONSTANTS.PROFILE.ADDRESS]
                    ? profile[CONSTANTS.PROFILE.ADDRESS]
                    : ""}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="col-sm-12 col-lg-8">
          <div
            className="card my-3 p-2"
            style={{
              boxShadow: "0px 5px 12px 0px rgba(0,0,0,0.1)",
            }}
          >
            <div className="card-body">
              <div className="d-flex justify-content-between px-0 mb-3">
                <h4 className="card-title mb-0 mx-1">Skills</h4>
                <div className="text-right">
                  <FontAwesomeIcon
                    icon={faPenToSquare}
                    size="1x"
                    onClick={() => setSkillsModalOpen(true)}
                    cursor="pointer"
                  />
                </div>
              </div>
              <div className="d-flex flex-wrap">
                {profile[CONSTANTS.PROFILE.SKILLS]?.map((ele, index) => (
                  <span
                    className="badge rounded-pill m-1 py-2 px-3"
                    style={{
                      border: "2px solid",
                      // backgroundColor: "#0096c7",
                      backgroundColor: "#296e85",
                      fontSize: 16,
                      fontWeight: "normal",
                    }}
                    key={index}
                  >
                    {ele}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div
            className="card my-3 p-2"
            style={{
              boxShadow: "0px 5px 12px 0px rgba(0,0,0,0.1)",
            }}
          >
            <div className="card-body">
              <div className="d-flex justify-content-between px-0 mb-3">
                <h4 className="card-title mb-0 mx-1">Experience Level</h4>
                <FontAwesomeIcon
                  icon={faPenToSquare}
                  size="1x"
                  onClick={() => setExpLevelModalOpen(true)}
                  cursor="pointer"
                />
              </div>
              <div className="d-flex flex-wrap">
                {profile[CONSTANTS.PROFILE.EXPERIENCE_LEVEL]?.map(
                  (ele, index) => (
                    <span
                      className="badge rounded-pill m-1 py-2 px-3"
                      style={{
                        border: "2px solid",
                        // backgroundColor: "#0096c7",
                        backgroundColor: "#296e85",
                        fontSize: 16,
                        fontWeight: "normal",
                      }}
                      key={index}
                    >
                      {ele}
                    </span>
                  )
                )}
              </div>
            </div>
          </div>
          <div
            className="card my-3 p-2"
            style={{
              boxShadow: "0px 5px 12px 0px rgba(0,0,0,0.1)",
            }}
          >
            <div className="card-body">
              <div className="d-flex justify-content-between px-0 mb-3">
                <h4 className="card-title mb-0 mx-1">Locations</h4>
                <FontAwesomeIcon
                  icon={faPenToSquare}
                  size="1x"
                  onClick={() => setLocationModalOpen(true)}
                  cursor="pointer"
                />
              </div>
              <div className="d-flex flex-wrap">
                {profile[CONSTANTS.PROFILE.PREFERRED_LOCATIONS]?.map(
                  (ele, index) => (
                    <span
                      className="badge rounded-pill m-1 py-2 px-3"
                      style={{
                        border: "2px solid",
                        // backgroundColor: "#0096c7",
                        backgroundColor: "#296e85",
                        fontSize: 16,
                        fontWeight: "normal",
                      }}
                      key={index}
                    >
                      {ele}
                    </span>
                  )
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      {locationModalOpen && (
        <LocationModal
          name={CONSTANTS.PROFILE.PREFERRED_LOCATIONS}
          options={CONSTANTS.CITIES}
          profile={props.profile}
          // setProfile={setProfile}
          setModalOpen={setLocationModalOpen}
          updateProfile={props.updateProfile}
        />
      )}
      {skillsModalOpen && (
        <SkillsModal
          name={CONSTANTS.PROFILE.SKILLS}
          options={CONSTANTS.SKILLS}
          profile={props.profile}
          // setProfile={setProfile}
          setModalOpen={setSkillsModalOpen}
          updateProfile={props.updateProfile}
        />
      )}
      {ExpLevelModalOpen && (
        <ExperienceLevelModal
          name={CONSTANTS.PROFILE.EXPERIENCE_LEVEL}
          options={CONSTANTS.EXPERIENCE_LEVEL}
          profile={props.profile}
          // setProfile={setProfile}
          setModalOpen={setExpLevelModalOpen}
          updateProfile={props.updateProfile}
        />
      )}
      {jobModeModalOpen && (
        <JobModeModal
          name={CONSTANTS.PROFILE.JOB_MODE}
          options={CONSTANTS.JOB_MODES}
          profile={props.profile}
          // setProfile={setProfile}
          setModalOpen={setJobModeModalOpen}
          updateProfile={props.updateProfile}
        />
      )}
      {profileModalOpen && (
        <ProfileModal
          profile={props.profile}
          // setProfile={setProfile}
          setModalOpen={setProfileModalOpen}
          updateProfile={props.updateProfile}
        />
      )}
      {/* <JobDescription /> */}
    </div>
  );
};

export default ProfilePage;
