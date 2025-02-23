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
			userProfile: null
		};
		this.sidebarHandler = this.sidebarHandler.bind(this);
		this.updateProfile = this.updateProfile.bind(this);
	}

	updateProfile = (profile) => {
		console.log('Update Request: ', profile);
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
		console.log(user);
		this.setState({
			currentPage: (
				<ProfilePage profile={user} updateProfile={this.updateProfile.bind(this)} />
			),
			sidebar: true,
			userProfile: user
		});
	};

	handleLogout = () => {
		localStorage.removeItem('token');
		localStorage.removeItem('userId');
		this.setState({
			sidebar: false
		});
	};

	switchPage(pageName) {
		const currentPage =
			pageName == 'ProfilePage' ? (
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
		var app;
		// console.log(this.state.sidebar)
		if (this.state.sidebar) {
			app = (
				<div className='main-page'>
					<Sidebar
						switchPage={this.switchPage.bind(this)}
						handleLogout={this.handleLogout}
					/>
					<div className='main'>
						<div className='content'>
							<div className=''>
								<h1
									className='text-center'
									style={{ marginTop: '2%', fontWeight: '300' }}
								>
									Application Tracking System
								</h1>
								{/* <span className="btn-icon ">
                <button className="btn btn-danger btn-icon"><i className="fas fa-plus"></i>&nbsp;New</button>
              </span> */}
							</div>
							{this.state.currentPage}
						</div>
					</div>
				</div>
			);
		} else {
			app = (
				<div className='main-page'>
					<div className='main'>
						<div className='content'>
							<h1
								className='text-center'
								style={{
									marginTop: 30,
									padding: 0.4 + 'em',
									fontWeight: '300'
								}}
							>
								Application Tracking System
							</h1>
							<div className=''>
								{/* <span className="btn-icon ">
              <button className="btn btn-danger btn-icon"><i className="fas fa-plus"></i>&nbsp;New</button>
            </span> */}
							</div>
							<LoginPage side={this.sidebarHandler} />
						</div>
					</div>
				</div>
			);
		}
		return app;
	}
}
