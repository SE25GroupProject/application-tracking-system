import React, { useState } from "react";
import {
  Button,
  Modal,
  ModalBody,
  ModalFooter,
  Form,
  Row,
  Col,
} from "react-bootstrap";
import Accordion from "react-bootstrap/Accordion";
import ModalHeader from "react-bootstrap/ModalHeader";
import axios from "axios";
import $ from "jquery";

const CoverLetter = (props) => {
  const [jobDescription, setJobDescription] = useState("");
  const [coverLetterTitle, setCoverLetterTitle] = useState("");
  const [coverLetter, setCoverLetter] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerateCoverLetter = async () => {
    setIsLoading(true);
    try {
      // const response = await axios.post('http://127.0.0.1:5000/cover_letter/' + props.idx, { "job_description": jobDescription, headers: {
      //     'Authorization': 'Bearer ' + localStorage.getItem('token'),
      //     'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
      //     'Access-Control-Allow-Credentials': 'true'
      // } });
      // setCoverLetter(response.data.response);
      $.ajax({
        url: "http://127.0.0.1:5000/cover_letter/" + props.idx,
        method: "POST",
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
          "Access-Control-Allow-Origin": "http://127.0.0.1:3000",
          "Access-Control-Allow-Credentials": "true",
          "Content-Type": "application/json",
        },
        data: JSON.stringify({ job_description: jobDescription }),
        dataType: "json",
        success: (message, textStatus, response) => {
          setCoverLetter(response.responseJSON.response);
        },
        complete: () => {
          setIsLoading(false);
        },
      });
    } catch (error) {
      console.error("Error generating cover letter:", error);
      alert("Failed to generate cover letter. Please try again.");
    }
  };

  const saveCoverLetter = () => {
    console.log(coverLetterTitle);
    const userId = localStorage.getItem("userId");

    axios
      .post(
        "http://localhost:5000/coverletters",
        { title: coverLetterTitle, content: coverLetter },
        {
          headers: {
            userid: userId,
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      )
      .then((res) => {
        props.closeModal(coverLetterTitle);
      })
      .catch((err) => {
        console.log(err.message);
      })
      .finally(() => {});
  };

  return (
    <Modal centered show={true} scrollable size="xl">
      <ModalHeader style={{ backgroundColor: "#296E85", color: "#fff" }}>
        <h4 className="mb-0 p-2">AI-Generated Cover Letter</h4>
      </ModalHeader>
      <ModalBody className="p-4">
        <Form.Group className="mb-3">
          <Form.Label>Job Description</Form.Label>
          <Form.Control
            as="textarea"
            rows={5}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Enter the job description here..."
          />
        </Form.Group>
        <Button
          className="custom-btn px-3 py-2 mb-3"
          onClick={handleGenerateCoverLetter}
          disabled={isLoading || !jobDescription.trim()}
        >
          {isLoading ? "Generating..." : "Generate Cover Letter"}
        </Button>
        {coverLetter && (
          <div className="mt-4">
            {/* <div style={{ fontSize: 22, fontWeight: '500' }}>Generated Cover Letter<br/><br/></div> */}

            <Form.Group className="mb-3" as={Row}>
              <Form.Label column sm={5}>
                Cover Letter Title
              </Form.Label>

              <Col sm={7}>
                <Form.Control
                  value={coverLetterTitle}
                  onChange={(e) => setCoverLetterTitle(e.target.value)}
                  placeholder="Enter cover letter title..."
                  required
                />
              </Col>
            </Form.Group>
            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header>Generated Cover Letter</Accordion.Header>
                <Accordion.Body>
                  <p
                    style={{
                      whiteSpace: "pre-wrap",
                      fontFamily: "serif",
                      fontSize: 12,
                    }}
                  >
                    {coverLetter}
                  </p>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
          </div>
        )}
      </ModalBody>
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
          onClick={saveCoverLetter}
        >
          Save!
        </Button>
      </ModalFooter>
    </Modal>
  );
};

export default CoverLetter;
