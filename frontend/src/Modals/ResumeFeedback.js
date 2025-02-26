import React, { useState, useEffect } from 'react';
import { Button, Modal, ModalBody, ModalFooter, Form } from 'react-bootstrap';
import ModalHeader from 'react-bootstrap/ModalHeader';
import $ from 'jquery';
import ReactMarkdown from 'react-markdown';

const ResumeFeedback = (props) => {
    const { setState } = props;
    const [resumeFeedback, setResumeFeedback] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        getResumeFeedback();
    }, []);

    const getResumeFeedback = async () => {
        setIsLoading(true);
        try {
            $.ajax({
                url: 'http://127.0.0.1:5000/resume-feedback/' + props.idx,
                method: 'GET',
                headers: {
                  'Authorization': 'Bearer ' + localStorage.getItem('token'),
                  'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
                  'Access-Control-Allow-Credentials': 'true',
                },
                success: (message, textStatus, response) => {
                    setResumeFeedback(response.responseJSON.feedback)
                }
            })
        } catch (error) {
            console.error('Error getting feedback:', error);
            alert('Error getting resume feedback. Please try again.');
        }
        setIsLoading(false);
    };

    return (
        <Modal centered show={true} scrollable size='xl'>
            <ModalHeader style={{ backgroundColor: '#296E85', color: '#fff' }}>
                <h4 className='mb-0 p-2'>AI-Generated Resume Feedback</h4>
            </ModalHeader>
            <ModalBody className='p-4'>
                {resumeFeedback && (
                    <div className='mt-4'>
                        {/* <div style={{ fontSize: 22, fontWeight: '500' }}>Generated Cover Letter<br/><br/></div> */}
                        
                            <ReactMarkdown>{resumeFeedback}</ReactMarkdown>
                        
                    </div>
                )}
            </ModalBody>
            <ModalFooter>
                <Button className='custom-btn px-3 py-2' onClick={() => setState(null)}>
                    Close
                </Button>
            </ModalFooter>
        </Modal>
    );
};

export default ResumeFeedback;
