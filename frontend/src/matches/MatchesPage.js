import React, { useState, useEffect } from 'react';
import JobTable from '../search/JobTable';

const Recommendations = () => {
	const [recommendedJobs, setRecommendedJobs] = useState([]);
	const [isFetchingJobs, setIsFetchingJobs] = useState(true);

	useEffect(() => {
		const lastJobFetchResults = localStorage.getItem('lastJobFetchResults');
		if (lastJobFetchResults) {
			setRecommendedJobs(JSON.parse(localStorage.getItem('lastJobFetchResults')));
			setIsFetchingJobs(false);
		} else {
			fetchRecommendations();
		}
	}, []);

	const fetchRecommendations = async () => {
		try {
			setIsFetchingJobs(true);
			const response = await fetch('http://localhost:5000/getRecommendations', {
				headers: {
					Authorization: 'Bearer ' + localStorage.getItem('token'),
					'Access-Control-Allow-Origin': 'http://localhost:3000',
					'Access-Control-Allow-Credentials': 'true'
				},
				method: 'GET'
			});
			const data = await response.json();
			if (data && data['error']) {
				throw new Error(data['error']);
			} else {
				localStorage.setItem('lastJobFetch', new Date().getTime());
				localStorage.setItem('lastJobFetchResults', JSON.stringify(data));
				setRecommendedJobs(data);
			}
		} catch (error) {
			console.log(error.message);
		} finally {
			setIsFetchingJobs(false);
		}
	};

	return (
		<div>
			<h2 class='d-flex justify-content-center my-5' style={{marginLeft: '9%'}}>Recommended Jobs</h2>
      <JobTable rows={recommendedJobs} loading={isFetchingJobs} emptyMessage="Make sure you've filled out your profile." />
		</div>
	);
};

export default Recommendations;
