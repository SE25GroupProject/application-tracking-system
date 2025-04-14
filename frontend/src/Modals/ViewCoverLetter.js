import React, { useEffect, useState } from "react";
import {
  Button,
  Modal,
  ModalBody,
  ModalFooter,
  Form,
  Row,
  Col,
  Spinner,
} from "react-bootstrap";
import Accordion from "react-bootstrap/Accordion";
import ModalHeader from "react-bootstrap/ModalHeader";
import axios from "axios";
import $ from "jquery";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit } from "@fortawesome/free-solid-svg-icons";

const ViewCoverLetter = (props) => {
  const [jobDescription, setJobDescription] = useState("");
  const [coverLetterTitle, setCoverLetterTitle] = useState("");
  const [coverLetter, setCoverLetter] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(async () => {
    try {
      $.ajax({
        url: "http://127.0.0.1:5000/coverletters/" + props.idx,
        method: "GET",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
          "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
          "Access-Control-Allow-Credentials": "true",
          "Content-Type": "application/json",
        },
        success: (message, textStatus, response) => {
          setCoverLetterTitle(message["coverletter"]["title"]);
          setCoverLetter(message["coverletter"]["content"]);
          setIsLoading(false);
        },
      });
    } catch (error) {
      console.error("Error getting cover letter:", error);
      alert("Retrieve cover letter. Please try again.");
    }
  }, []);

  const updateCoverLetter = () => {
    const userId = localStorage.getItem("userId");

    axios
      .put(
        "http://localhost:5000/coverletters/" + props.idx,
        { title: coverLetterTitle, content: coverLetter },
        {
          headers: {
            userid: userId,
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      )
      .then((res) => {
        alert("Cover letter successfully saved!");
      })
      .catch((err) => {
        console.log(err.message);
      });
  };

  return (
    <Modal centered show={true} scrollable size="xl">
      <ModalHeader style={{ backgroundColor: "#296E85", color: "#fff" }}>
        <h4 className="mb-0 p-2">AI-Generated Cover Letter</h4>
      </ModalHeader>
      <ModalBody className="p-4">
        <div className="mt-4">
          {isLoading ? (
            <div>
              <Spinner />
              <h4>Loading...</h4>
            </div>
          ) : (
            <>
              <Form.Group className="mb-3" as={Row}>
                <Form.Label column sm={5}>
                  Title
                </Form.Label>

                <Col sm={7}>
                  {isEditing ? (
                    <Form.Control
                      value={coverLetterTitle}
                      onChange={(e) => setCoverLetterTitle(e.target.value)}
                      placeholder="Enter cover letter title..."
                      required
                    />
                  ) : (
                    <h4>{coverLetterTitle}</h4>
                  )}
                </Col>
              </Form.Group>
              <Accordion>
                <Accordion.Item eventKey="0">
                  <Accordion.Header>Generated Cover Letter</Accordion.Header>
                  <Accordion.Body>
                    {isEditing ? (
                      <Form.Control
                        as="textarea"
                        rows={20}
                        value={coverLetter}
                        onChange={(e) => setCoverLetter(e.target.value)}
                        placeholder="Enter cover letter title..."
                        required
                      />
                    ) : (
                      <p
                        style={{
                          whiteSpace: "pre-wrap",
                          fontFamily: "serif",
                          fontSize: 12,
                        }}
                      >
                        {coverLetter}
                      </p>
                    )}
                  </Accordion.Body>
                </Accordion.Item>
              </Accordion>{" "}
            </>
          )}
        </div>
      </ModalBody>
      {isEditing ? (
        <ModalFooter>
          <Button
            className="custom-btn px-3 py-2"
            onClick={() => setIsEditing(false)}
          >
            Cancel
          </Button>
          <Button
            className="custom-btn alt px-3 py-2"
            disabled={!coverLetterTitle}
            onClick={() => {
              updateCoverLetter();
              setIsEditing(false);
            }}
          >
            Save!
          </Button>

          <Button
            className="custom-btn alt px-3 py-2"
            disabled={!coverLetterTitle}
            onClick={() => {
              updateCoverLetter();
              props.closeModal(coverLetterTitle);
            }}
          >
            Save and Close!
          </Button>
        </ModalFooter>
      ) : (
        <ModalFooter>
          <Button
            className="custom-btn px-3 py-2"
            onClick={() => props.closeModal(null)}
          >
            Close
          </Button>
          <Button
            className="custom-btn alt px-3 py-2"
            disabled={!coverLetterTitle}
            onClick={() => setIsEditing(true)}
          >
            Edit
          </Button>
        </ModalFooter>
      )}
    </Modal>
  );
};

export default ViewCoverLetter;
