import './static/App.css';

import React from 'react';
import Sidebar from './sidebar/Sidebar';
import ApplicationPage from './application/ApplicationPage';
import SearchPage from './search/SearchPage';
import LoginPage from './login/LoginPage';
import ManageResumePage from './resume/ManageResumePage';
import ProfilePage from './profile/ProfilePage';
import axios from 'axios';
import MatchesPage from './matches/MatchesPage';

export default class App extends React.Component {
	constructor(props) {
		super(props);
		let mapRouter = {
			SearchPage: <SearchPage />,
			ApplicationPage: <ApplicationPage />,
			LoginPage: <LoginPage />,
			ManageResumePage: <ManageResumePage />,
			ProfilePage: <ProfilePage />,
			MatchesPage: <MatchesPage />
		};
		this.state = {
			currentPage: <LoginPage />,
			mapRouter: mapRouter,
			sidebar: false,
			userProfile: null,
			showLogoutModal: false // ✅ State to control the custom modal
		};
		this.sidebarHandler = this.sidebarHandler.bind(this);
		this.updateProfile = this.updateProfile.bind(this);
	}

	updateProfile = (profile) => {
		this.setState({
			userProfile: profile,
			currentPage: <ProfilePage profile={profile} updateProfile={this.updateProfile} />
		});
	};

	async componentDidMount() {
		if (localStorage.getItem('token')) {
			const userId = localStorage.getItem('userId');
			await axios
				.get('http://localhost:5000/getProfile', {
					headers: {
						userid: userId,
						Authorization: `Bearer ${localStorage.getItem('token')}`
					}
				})
				.then((res) => {
					this.sidebarHandler(res.data);
				})
				.catch((err) => console.log(err.message));
		}
	}

	sidebarHandler = (user) => {
		this.setState({
			currentPage: (
				<ProfilePage profile={user} updateProfile={this.updateProfile.bind(this)} />
			),
			sidebar: true,
			userProfile: user
		});
	};

	// ✅ Show Logout Modal
	handleLogout = () => {
		this.setState({ showLogoutModal: true });
	};

	// ✅ Confirm Logout
	confirmLogout = () => {
		localStorage.removeItem('token');
		localStorage.removeItem('userId');
		this.setState({
			sidebar: false,
			showLogoutModal: false
		});
	};

	// ✅ Cancel Logout
	cancelLogout = () => {
		this.setState({ showLogoutModal: false });
	};

	switchPage(pageName) {
		const currentPage =
			pageName === 'ProfilePage' ? (
				<ProfilePage
					profile={this.state.userProfile}
					updateProfile={this.updateProfile.bind(this)}
				/>
			) : (
				this.state.mapRouter[pageName]
			);
		this.setState({
			currentPage: currentPage
		});
	}

	render() {
		const { showLogoutModal } = this.state;

		return (
			<div>
				{this.state.sidebar ? (
					<div className='main-page'>
						<Sidebar
							switchPage={this.switchPage.bind(this)}
							handleLogout={this.handleLogout}
						/>
						<div className='main'>
							<div className='container'>
								<h1 className='text-center' style={{ marginTop: '2%', fontWeight: '300'}}>
									Application Tracking System
								</h1>
								{this.state.currentPage}
							</div>
						</div>
					</div>
				) : (
					<div className='main'>
						<div className='content'>
							<h1
								className='text-center'
								style={{
									marginTop: 30,
									padding: '0.4em',
									fontWeight: '300'
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
					<div className='modal-overlay'>
						<div className='custom-modal'>
							<h2>Confirm Logout</h2>
							<p>Are you sure you want to logout?</p>
							<div className='modal-buttons'>
								<button className='btn cancel-btn' onClick={this.cancelLogout}>
									Cancel
								</button>
								<button className='btn logout-btn' onClick={this.confirmLogout}>
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
