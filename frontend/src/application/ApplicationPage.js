import React, { useState, useEffect, useCallback } from 'react';
import { Card, Col, Container, Row, Modal } from 'react-bootstrap';
import Button from 'react-bootstrap/Button';

const ApplicationsList = ({ applicationList, handleCardClick, selectedApplication, handleUpdateDetails, handleDeleteApplication }) => {
  const [closeModal, setCloseModal] = useState(true);
  const [job, setJob] = useState();
  const [company, setCompany] = useState();
  const [location, setLocation] = useState();
  const [status, setStatus] = useState();
  const [date, setDate] = useState();
  const [jobLink, setJobLink] = useState();
  const [isCreate, setIsCreate] = useState();

  const findStatus = (value) => {
    let status = '';
    if (value === '1') status = '💡 Wish List';
    else if (value === '2') status = '👤 Waiting for referral';
    else if (value === '3') status = '✅ Applied';
    else if (value === '4') status = '❌ Rejected';
    return status || "N/A";
  };

  return (
    <>
      <Button
        style={{
          marginLeft: "11%",
          marginTop: "4%",
          backgroundColor: "#296E85",
          borderRadius: "8px",
          border: "none",
        }}
        size="lg"
        onClick={() => {
          handleCardClick(null);
          setCloseModal(false);
          setIsCreate(true);
          setJob(null);
          setCompany(null);
          setLocation(null);
          setStatus(null);
          setDate(null);
          setJobLink(null);
        }}
      >
        + Add New Application
      </Button>

      <Container style={{ marginTop: "30px" }}>
        <Row>
          {applicationList.map((jobListing) => (
            <Col key={jobListing.id} md={12} style={{ marginBottom: "20px" }}>
              <Card
                style={{
                  marginLeft: "10%",
                  borderColor: "#e0e0e0",
                  borderRadius: "12px",
                  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
                  transition: "0.3s",
                  cursor: "pointer",
                  width:"103%",
                  padding: "15px",
              
                }}
                onClick={() => {
                  handleCardClick(jobListing);
                  setCloseModal(false);
                  setJob(jobListing?.jobTitle);
                  setCompany(jobListing?.companyName);
                  setLocation(jobListing?.location);
                  setStatus(jobListing?.status);
                  setDate(jobListing?.date);
                  setJobLink(jobListing?.jobLink);
                  setIsCreate(false);
                }}
              >
                <Card.Body>
                  <Row className="align-items-center justify-content-between">

                    {/* Left Side - Job Title & Company */}
                    <Col sm={3}>
                      <Card.Title style={{ fontSize: "20px", fontWeight: "bold", color: "#34495e", marginBottom: "4px" }}>
                        {jobListing?.jobTitle || "N/A"}
                      </Card.Title>
                      <Card.Subtitle style={{ fontSize: "16px", color: "#7f8c8d" }}>
                        {jobListing?.companyName || "N/A"}
                      </Card.Subtitle>
                    </Col>

                    {/* Right Side - Location, Date, Status in One Row */}
                    <Col sm={9}>
  <div style={{ 
    display: "flex", 
    justifyContent: "space-between", 
    alignItems: "center", 
    width: "100%", 
    gap: "20px", 
    flexWrap: "nowrap", // ❌ Prevents wrapping
    overflow: "hidden"
  }}>
    {/* Location */}
    <div style={{ 
      display: "flex", 
      alignItems: "center", 
      minWidth: "277px", 
      maxWidth: "277px", 
      whiteSpace: "nowrap", 
      overflow: "hidden", 
      textOverflow: "ellipsis" 
    }}>
      <span role="img" aria-label="location">📍</span>
      <strong style={{ marginLeft: "5px" }}>Location:</strong>
      <span style={{ marginLeft: "5px" }}>{jobListing?.location || "N/A"}</span>
    </div>

    {/* Date */}
    <div style={{ 
      display: "flex", 
      alignItems: "center", 
      minWidth: "200px", 
      maxWidth: "150px", 
      whiteSpace: "nowrap", 
      overflow: "hidden", 
      textOverflow: "ellipsis" 
    }}>
      <span role="img" aria-label="calendar">📅</span>
      <strong style={{ marginLeft: "5px" }}>Date:</strong>
      <span style={{ marginLeft: "5px" }}>{jobListing?.date || "N/A"}</span>
    </div>

    {/* Status */}
    <div style={{ 
      display: "flex", 
      alignItems: "center", 
      minWidth: "290px", 
      maxWidth: "290px", 
      whiteSpace: "nowrap", 
      overflow: "hidden", 
      textOverflow: "ellipsis" 
    }}>
      <span role="img" aria-label="status">📊</span>
      <strong style={{ marginLeft: "5px" }}>Status:</strong>
      <span style={{ marginLeft: "5px" }}>{findStatus(jobListing?.status) || "N/A"}</span>
    </div>
  </div>
</Col>

                  </Row>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </Container>

      <Modal show={!closeModal} onHide={() => setCloseModal(true)}>
        <Modal.Header closeButton>
          <Modal.Title>{isCreate ? 'Add New Application' : 'Update Details'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="form-group">
            <label className='col-form-label'>Job Title</label>
            <input type="text" className="form-control" placeholder="Job Title" value={job} onChange={(e) => setJob(e.target.value)} />
          </div>
          <div className="form-group">
            <label className='col-form-label'>Company Name</label>
            <input type="text" className="form-control" placeholder="Company Name" value={company} onChange={(e) => setCompany(e.target.value)} />
          </div>
          <div className='form-group'>
            <label className='col-form-label'>Date</label>
            <input type='date' className='form-control' value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div className='form-group'>
            <label className='col-form-label'>Job Link</label>
            <input type='text' className='form-control' placeholder='Job Link' value={jobLink} onChange={(e) => setJobLink(e.target.value)} />
          </div>
          <div className='form-group'>
            <label className='col-form-label'>Location</label>
            <input type='text' className='form-control' placeholder='Location' value={location} onChange={(e) => setLocation(e.target.value)} />
          </div>
          <div className='input-group mb-3'>
            <div className='input-group-prepend'>
              <label className='input-group-text'>Application Type</label>
            </div>
            <select className='custom-select' value={status} onChange={(e) => setStatus(e.target.value)}>
              <option>Choose...</option>
              <option value='1'>Wish list</option>
              <option value='2'>Waiting Referral</option>
              <option value='3'>Applied</option>
              <option value='4'>Rejected</option>
            </select>
          </div>
        </Modal.Body>
        <Modal.Footer>
          {!isCreate && (
            <Button variant="danger" onClick={() => { handleDeleteApplication(selectedApplication); setCloseModal(true); }}>
              Delete
            </Button>
          )}
          <Button variant="success" onClick={() => {
            handleUpdateDetails(selectedApplication?.id, job, company, location, date, status, jobLink);
            setCloseModal(true);
          }}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

const ApplicationPage = () => {
  const [applicationList, setApplicationList] = useState([]);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [isChanged, setISChanged] = useState(true);

  useEffect(() => {
    if (isChanged) {
      fetch('http://127.0.0.1:5000/applications', {
        headers: {
          Authorization: 'Bearer ' + localStorage.getItem('token'),
          'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
          'Access-Control-Allow-Credentials': 'true',
        },
        method: 'GET',
      })
        .then((response) => response.json())
        .then((data) => setApplicationList(data));
    }
  }, [isChanged]);

  const handleCardClick = (jobListing) => setSelectedApplication(jobListing);

  const handleUpdateDetails = useCallback((id, job, company, location, date, status, jobLink) => {
    let application = { id: id || null, jobTitle: job, companyName: company, location, date, status, jobLink };

    const url = id ? `http://127.0.0.1:5000/applications/${id}` : 'http://127.0.0.1:5000/applications';
    const method = id ? 'PUT' : 'POST';

    fetch(url, {
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true',
        'Content-Type': 'application/json',
      },
      method,
      body: JSON.stringify({ application })
    })
      .then((response) => response.json())
      .then((data) => {
        if (!id) application.id = data.id;
        setApplicationList((prev) => id ? prev.map(app => app.id === id ? application : app) : [...prev, application]);
      })
      .catch((error) => alert(id ? 'Update Failed!' : 'Adding application failed!'));
  }, []);

  const handleDeleteApplication = (application) => {
    fetch(`http://127.0.0.1:5000/applications/${application?.id}`, {
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('token'),
        'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
        'Access-Control-Allow-Credentials': 'true',
        'Content-Type': 'application/json',
      },
      method: 'DELETE',
    })
      .then(() => setISChanged(true))
      .catch(() => alert('Error while deleting the application!'));

    setISChanged(false);
    setSelectedApplication(null);
  };

  return <ApplicationsList
    applicationList={applicationList}
    handleCardClick={handleCardClick}
    selectedApplication={selectedApplication}
    handleUpdateDetails={handleUpdateDetails}
    handleDeleteApplication={handleDeleteApplication}
  />;
};

export default ApplicationPage;
