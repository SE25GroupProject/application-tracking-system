import React, { Component } from "react";
import { Alert, Modal, Tab, Tabs } from "react-bootstrap";
import $ from "jquery";
import "../static/resume.css";
import GenerateCoverLetter from "../Modals/GenerateCoverLetter";
import ResumeFeedback from "../Modals/ResumeFeedback";
import ViewCoverLetter from "../Modals/ViewCoverLetter";

export default class ManageResumePage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      resumeFileNames: [],
      coverLetterFileNames: [],
      loading: false,
      generateCoverLetterIdx: null,
      viewCoverLetterIdx: null,
      resumeFeedbackIdx: null,
      showCoverLetterCreatedAlert: "",
    };
  }

  updateCoverLetters() {
    $.ajax({
      url: "http://127.0.0.1:5000/coverletters",
      method: "GET",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      credentials: "include",
      success: (message, textStatus, response) => {
        console.log(message);
        this.setState({
          coverLetterFileNames: message.filenames,
        });
      },
    });
  }

  deleteCoverLetter(coverletter_idx) {
    $.ajax({
      url: "http://127.0.0.1:5000/coverletters/" + coverletter_idx,
      method: "DELETE",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      success: (message, textStatus, response) => {
        console.log(message);
        this.updateCoverLetters();
      },
    });
  }

  getFiles() {
    $.ajax({
      url: "http://127.0.0.1:5000/resume",
      method: "GET",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      credentials: "include",
      success: (message, textStatus, response) => {
        console.log(message);
        this.setState({
          resumeFileNames: message.filenames,
        });
      },
    });

    this.updateCoverLetters();
  }

  openGenerateCoverLetterModal = (idx) => {
    this.setState({ generateCoverLetterIdx: idx });
  };

  closeGenerateCoverLetterModal = (savedLetter = "") => {
    this.setState({ generateCoverLetterIdx: null });

    if (savedLetter) {
      this.updateCoverLetters();
      this.setState({ showCoverLetterCreatedAlert: savedLetter });

      setTimeout(() => {
        this.setState({ showCoverLetterCreatedAlert: "" });
      }, 2000);
    }
  };

  openViewCoverLetterModal = (idx) => {
    this.setState({ viewCoverLetterIdx: idx });
  };

  closeViewCoverLetterModal = (editedLetter = "") => {
    this.setState({ viewCoverLetterIdx: null });
    this.updateCoverLetters();

    if (editedLetter) {
      this.setState({ showSavedAlert: editedLetter });

      setTimeout(() => {
        this.setState({ showSavedAlert: "" });
      }, 2000);
    }
  };

  openResumeFeedbackModal = (idx) => {
    this.setState({ resumeFeedbackIdx: idx });
  };

  closeResumeFeedbackModal = () => {
    this.setState({ resumeFeedbackIdx: null });
  };

  previewResume(resume_idx) {
    $.ajax({
      url: "http://127.0.0.1:5000/resume/" + resume_idx,
      method: "GET",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      xhrFields: { responseType: "blob" },
      credentials: "include",
      success: (message, textStatus, response) => {
        console.log(message);
        if (message) {
          window.open(URL.createObjectURL(message), "_blank");
        }
      },
    });
  }

  previewCoverLetter(coverletter_idx) {
    $.ajax({
      url: "http://127.0.0.1:5000/resume/" + coverletter_idx,
      method: "GET",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      xhrFields: { responseType: "blob" },
      credentials: "include",
      success: (message, textStatus, response) => {
        console.log(message);
        if (message) {
          window.open(URL.createObjectURL(message), "_blank");
        }
      },
    });
  }

  deleteResume(resume_idx) {
    $.ajax({
      url: "http://127.0.0.1:5000/resume/" + resume_idx,
      method: "DELETE",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      success: (message, textStatus, response) => {
        this.state.resumeFileNames.splice(resume_idx, 1);
        console.log(response.responseJSON.success);
        this.getFiles();
      },
    });
  }

  uploadResume = (e) => {
    e.preventDefault();

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".pdf"; // Adjust allowed file types if needed

    fileInput.addEventListener("change", (event) => {
      if (event.target.files.length == 0) {
        return;
      }

      this.setState({ loading: true });
      let formData = new FormData();
      const file = event.target.files[0];
      formData.append("file", file);
      $.ajax({
        url: "http://127.0.0.1:5000/resume",
        method: "POST",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
          "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
          "Access-Control-Allow-Credentials": "true",
        },
        data: formData,
        contentType: false,
        cache: false,
        processData: false,
        success: (msg) => {
          console.log("Upload successful:", msg);
          this.setState({
            resumeFileNames: [...this.state.resumeFileNames, file.name],
          });
        },
      }).always(() => this.setState({ loading: false }));
    });

    fileInput.click();
  };

  componentDidMount() {
    this.getFiles();
  }

  componentWillUnmount() {
    if (this.state.previewUrl) {
      URL.revokeObjectURL(this.state.previewUrl);
    }
  }

  render() {
    return (
      <div className="pagelayout">
        {this.state.showCoverLetterCreatedAlert && (
          <Alert variant="success">
            {this.state.showCoverLetterCreatedAlert} was saved successfully!
          </Alert>
        )}

        <Tabs defaultActiveKey="resume">
          <Tab eventKey="resume" title="Resumes" className="pt-3">
            <form id="upload-file" method="post" encType="multipart/form-data">
              <button
                className="upload-file-btn"
                onClick={(event) => {
                  if (!this.state.loading) {
                    this.uploadResume(event);
                  }
                }}
                disabled={this.state.loading}
                type="button"
                style={{
                  display: "block",
                  margin: "0 auto",
                }}
              >
                {this.state.loading ? "Uploading..." : "Upload New"}
              </button>

              <div style={{ margin: "1.5em" }}></div>
              <div>
                <h2>Uploaded Resumes</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Documents</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {this.state.resumeFileNames.map((fileName, index) => (
                      <tr key={index}>
                        <td>{fileName}</td>
                        <td>
                          <button
                            id="view-file-btn"
                            onClick={() => this.previewResume(index)}
                            type="button"
                          >
                            Preview
                          </button>
                          <button
                            id="view-file-btn"
                            onClick={() => this.openResumeFeedbackModal(index)}
                            type="button"
                          >
                            View Feedback
                          </button>
                          <button
                            id="view-file-btn"
                            onClick={() =>
                              this.openGenerateCoverLetterModal(index)
                            }
                            type="button"
                          >
                            Generate Cover Letter
                          </button>
                          <button
                            id="delete-file-btn"
                            onClick={() => this.deleteResume(index)}
                            type="button"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </form>
          </Tab>
          <Tab eventKey="coverletters" title="Cover Letters" className="pt-3">
            <form id="upload-file" method="post" encType="multipart/form-data">
              <div style={{ margin: "1.5em" }}></div>
              <div>
                <h2>Uploaded Cover Letters</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Cover Letters</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {this.state.coverLetterFileNames.map(
                      (coverletterName, index) => (
                        <tr key={index}>
                          <td>{coverletterName}</td>
                          <td>
                            <button
                              id="view-file-btn"
                              onClick={() =>
                                this.openViewCoverLetterModal(index)
                              }
                              type="button"
                            >
                              View/Edit Cover Letter
                            </button>
                            <button
                              id="delete-file-btn"
                              onClick={() => this.deleteCoverLetter(index)}
                              type="button"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </form>
          </Tab>
        </Tabs>

        {this.state.generateCoverLetterIdx !== null && (
          <GenerateCoverLetter
            closeModal={this.closeGenerateCoverLetterModal}
            idx={this.state.generateCoverLetterIdx}
          />
        )}
        {this.state.viewCoverLetterIdx !== null && (
          <ViewCoverLetter
            closeModal={this.closeViewCoverLetterModal}
            idx={this.state.viewCoverLetterIdx}
          />
        )}
        {this.state.resumeFeedbackIdx !== null && (
          <ResumeFeedback
            setState={this.closeResumeFeedbackModal}
            idx={this.state.resumeFeedbackIdx}
          />
        )}
      </div>
    );
  }
}
