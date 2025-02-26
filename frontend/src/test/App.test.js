import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import App from '../App';
import axios from 'axios';

// --- Mocks for Child Components ---
// These mocks ensure predictable output in tests.
jest.mock('../login/LoginPage', () => () => <div data-testid="login-page">Login</div>);
jest.mock('../sidebar/Sidebar', () => (props) => (
  <div data-testid="sidebar">
    <button onClick={() => props.switchPage('ProfilePage')}>Profile</button>
    <button onClick={() => props.switchPage('SearchPage')}>Search</button>
    <button onClick={() => props.switchPage('MatchesPage')}>Matches</button>
    <button onClick={() => props.switchPage('ApplicationPage')}>Applications</button>
    <button onClick={() => props.switchPage('ManageResumePage')}>Manage</button>
    <button onClick={props.handleLogout}>LogOut</button>
  </div>
));
jest.mock('../profile/ProfilePage', () => (props) => <div data-testid="profile-page">Profile</div>);
jest.mock('../search/SearchPage', () => () => <div data-testid="search-page">Search</div>);
jest.mock('../application/ApplicationPage', () => () => <div data-testid="application-page">Application</div>);
jest.mock('../resume/ManageResumePage', () => () => <div data-testid="manage-resume-page">Uploaded Documents</div>);
jest.mock('../matches/MatchesPage', () => () => <div data-testid="matches-page">Matches</div>);

// --- Mock axios ---
jest.mock('axios');

describe('App Component', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  // 1. Header is rendered.
  test('renders header "Application Tracking System"', () => {
    render(<App />);
    const headers = screen.getAllByText(/Application Tracking System/i);
    expect(headers.length).toBeGreaterThan(0);
  });

  // 2. Renders LoginPage when no token is present.
  test('renders LoginPage when no token is present', () => {
    render(<App />);
    const loginPage = screen.getByTestId('login-page');
    expect(loginPage).toBeInTheDocument();
  });

  // 3. When token exists, axios.get is called and Sidebar is rendered.
  test('renders Sidebar when token exists and profile is fetched', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    });
  });

  // 4. Clicking "LogOut" displays the logout modal.
  test('displays logout modal when LogOut is clicked', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      const logoutBtn = screen.getByText(/LogOut/i);
      fireEvent.click(logoutBtn);
    });
    const modalHeader = screen.getByText(/Confirm Logout/i);
    expect(modalHeader).toBeInTheDocument();
  });

  // 5. Confirming logout removes token and hides the Sidebar.
  // Modified to scope the "Logout" button search within the modal.
  test('confirming logout removes token and hides sidebar', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      const logoutBtn = screen.getByText(/LogOut/i);
      fireEvent.click(logoutBtn);
    });
    // Scope search within the modal overlay to find the confirm button.
    const modalOverlay = screen.getByText(/Confirm Logout/i).closest('.modal-overlay');
    const confirmBtn = within(modalOverlay).getByText(/^Logout$/i);
    fireEvent.click(confirmBtn);
    await waitFor(() => {
      expect(localStorage.getItem('token')).toBeNull();
      expect(screen.queryByTestId('sidebar')).toBeNull();
    });
  });

  // 6. Canceling logout hides the logout modal.
  test('cancel logout hides the logout modal', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      const logoutBtn = screen.getByText(/LogOut/i);
      fireEvent.click(logoutBtn);
    });
    const cancelBtn = screen.getByText(/Cancel/i);
    fireEvent.click(cancelBtn);
    await waitFor(() => {
      expect(screen.queryByText(/Confirm Logout/i)).toBeNull();
    });
  });

  // 7. Clicking "Profile" sets currentPage to ProfilePage.
  // Modified to use getByRole for the button.
  test('switchPage sets currentPage to ProfilePage when "Profile" is clicked', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'Jane Doe' } });
    render(<App />);
    await waitFor(() => {
      const profileBtn = screen.getByRole('button', { name: 'Profile' });
      fireEvent.click(profileBtn);
    });
    const profilePage = screen.getByTestId('profile-page');
    expect(profilePage).toBeInTheDocument();
  });

  // 8. Clicking "Search" sets currentPage to SearchPage.
  // Modified to use getByRole.
  test('switchPage sets currentPage to SearchPage when "Search" is clicked', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      const searchBtn = screen.getByRole('button', { name: 'Search' });
      fireEvent.click(searchBtn);
    });
    const searchPage = screen.getByTestId('search-page');
    expect(searchPage).toBeInTheDocument();
  });

  // 9. Clicking "Applications" sets currentPage to ApplicationPage.
  // Modified to use getByRole.
  test('switchPage sets currentPage to ApplicationPage when "Applications" is clicked', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      const appBtn = screen.getByRole('button', { name: 'Applications' });
      fireEvent.click(appBtn);
    });
    const applicationPage = screen.getByTestId('application-page');
    expect(applicationPage).toBeInTheDocument();
  });

  // 10. Clicking "Manage" sets currentPage to ManageResumePage.
  // Modified to use getByRole.
  test('switchPage sets currentPage to ManageResumePage when "Manage" is clicked', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      const manageBtn = screen.getByRole('button', { name: 'Manage' });
      fireEvent.click(manageBtn);
    });
    const managePage = screen.getByTestId('manage-resume-page');
    expect(managePage).toBeInTheDocument();
  });

  // 11. Clicking "Matches" sets currentPage to MatchesPage.
  // Modified to use getByRole.
  test('switchPage sets currentPage to MatchesPage when "Matches" is clicked', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      const matchesBtn = screen.getByRole('button', { name: 'Matches' });
      fireEvent.click(matchesBtn);
    });
    const matchesPage = screen.getByTestId('matches-page');
    expect(matchesPage).toBeInTheDocument();
  });

  // 12. Renders main structure elements with correct classes.
  test('renders main structure elements with correct classes', () => {
    render(<App />);
    expect(document.querySelector('.main-page')).toBeInTheDocument();
    expect(document.querySelector('.main')).toBeInTheDocument();
    expect(document.querySelector('.content')).toBeInTheDocument();
  });

  // 13. Logout modal is not rendered by default.
  test('logout modal is not rendered by default', () => {
    render(<App />);
    expect(document.querySelector('.modal-overlay')).toBeNull();
  });

  // 14. updateProfile updates userProfile and renders ProfilePage.
  test('updateProfile updates userProfile and renders ProfilePage', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'Jane Doe' } });
    render(<App />);
    await waitFor(() => {
      const profilePage = screen.getByTestId('profile-page');
      expect(profilePage).toBeInTheDocument();
    });
  });

  // 15. When token exists, axios.get is called in componentDidMount.
  test('calls axios.get in componentDidMount when token exists', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalled();
    });
  });

  // 16. When no token exists, axios.get is not called.
  test('does not call axios.get when no token exists', () => {
    render(<App />);
    expect(axios.get).not.toHaveBeenCalled();
  });

  // 17. sidebarHandler sets sidebar to true and renders Sidebar.
  test('sidebarHandler sets sidebar state to true and renders Sidebar', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    });
  });

  // 18. Renders LoginPage inside the "content" div when sidebar is false.
  test('renders LoginPage inside content div when sidebar is false', () => {
    localStorage.removeItem('token');
    const { container } = render(<App />);
    const contentDiv = container.querySelector('.content');
    expect(contentDiv).toHaveTextContent('Login');
  });

  // 19. Logout modal displays correct content when active.
  test('renders logout modal with proper content when active', async () => {
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('userId', '123');
    axios.get.mockResolvedValueOnce({ data: { name: 'John Doe' } });
    render(<App />);
    await waitFor(() => {
      fireEvent.click(screen.getByText(/LogOut/i));
    });
    expect(screen.getByText(/Confirm Logout/i)).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to logout/i)).toBeInTheDocument();
  });

  // 20. Renders custom modal styling in a <style> tag.
  test('renders custom modal styling in a <style> tag', () => {
    render(<App />);
    const styleTag = document.querySelector('style');
    expect(styleTag).toBeInTheDocument();
    expect(styleTag.textContent).toMatch(/\.modal-overlay/);
  });
});
