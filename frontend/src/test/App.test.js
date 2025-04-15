import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
} from "@testing-library/react";
import App from "../App";
import axios from "axios";
import { CONSTANTS } from "../data/Constants";

// --- Test Data
const profile0 = {
  address: null,
  email: "person@gmail.com",
  fullName: "Person",
  institution: null,
  job_levels: [],
  locations: [],
  phone_number: null,
  profileName: "Default Profile",
  profileid: 0,
  skills: [],
};

const profile1 = {
  address: null,
  email: "person@gmail.com",
  fullName: "Person",
  institution: null,
  job_levels: [],
  locations: [],
  phone_number: null,
  profileName: "Profile 1",
  profileid: 1,
  skills: [],
};

const profile2 = {
  address: null,
  email: "person@gmail.com",
  fullName: "Person",
  institution: null,
  job_levels: [],
  locations: [],
  phone_number: null,
  profileName: "Profile 2",
  profileid: 2,
  skills: [],
};

const initialProfileList = [
  { isDefault: true, profileName: "Default Profile", profileid: 0 },
  { isDefault: false, profileName: "Profile 1", profileid: 1 },
  { isDefault: false, profileName: "Profile 2", profileid: 2 },
];

let profiles = [profile0, profile1, profile2];
let profileList = initialProfileList;
let defaultProfile = 0;

const getImplementation = (input) => {
  if (input === "http://localhost:5000/getProfile") {
    return Promise.resolve({
      data: profiles[defaultProfile],
    });
  } else if (/localhost:5000\/getProfile\/(?<profileid>[\d])/.test(input)) {
    let found = input.match(/localhost:5000\/getProfile\/(?<profileid>[\d])/);
    return Promise.resolve({
      data: profiles[found.groups.profileid],
    });
  } else if (input === "http://localhost:5000/getProfileList") {
    return Promise.resolve({
      data: {
        [CONSTANTS.PROFILE.PROFILE_LIST]: profileList,
        [CONSTANTS.PROFILE.DEFAULT_PROFILE]: defaultProfile,
      },
    });
  } else {
    console.log(input);
  }
};

const postImplementation = (input) => {};

// --- Mocks for Child Components ---
// These mocks ensure predictable output in tests.
jest.mock("../login/LoginPage", () => () => (
  <div data-testid="login-page">Login</div>
));
// jest.mock("../sidebar/Sidebar", () => (props) => (
//   <div data-testid="sidebar">
//     <button onClick={() => props.switchPage("ProfilePage")}>Profile</button>
//     <button onClick={() => props.switchPage("SearchPage")}>Search</button>
//     <button onClick={() => props.switchPage("MatchesPage")}>Matches</button>
//     <button onClick={() => props.switchPage("ApplicationPage")}>
//       Applications
//     </button>
//     <button onClick={() => props.switchPage("ManageResumePage")}>Manage</button>
//     <button onClick={props.handleLogout}>LogOut</button>
//   </div>
// ));
// jest.mock("../profile/ProfilePage", () => (props) => (
//   <div data-testid="profile-page">Profile</div>
// ));
jest.mock("../search/SearchPage", () => () => (
  <div data-testid="search-page">Search</div>
));
jest.mock("../application/ApplicationPage", () => () => (
  <div data-testid="application-page">Application</div>
));
// To test this page, React Markdown will need to be removed, or the page will need to be copied without it
jest.mock("../resume/ManageResumePage", () => () => (
  <div data-testid="manage-resume-page">Uploaded Documents</div>
));
jest.mock("../matches/MatchesPage", () => () => (
  <div data-testid="matches-page">Matches</div>
));

// --- Mock axios ---
jest.mock("axios");

// axios.get.mockImplementation(() =>
//   Promise.resolve({
//     data: {
//       [CONSTANTS.PROFILE.PROFILE_LIST]: profileList,
//       [CONSTANTS.PROFILE.DEFAULT_PROFILE]: 0,
//     },
//   })
// );

describe("App Component, not logged in", () => {
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
  test("renders LoginPage when no token is present", () => {
    render(<App />);
    const loginPage = screen.getByTestId("login-page");
    expect(loginPage).toBeInTheDocument();
  });

  // 3. When no token exists, axios.get is not called.
  test("does not call axios.get when no token exists", () => {
    render(<App />);
    expect(axios.get).not.toHaveBeenCalled();
  });
});

describe("App Component, logged in", () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();

    localStorage.setItem("token", "dummy-token");
    localStorage.setItem("userId", "123");
    axios.get.mockImplementation(getImplementation);
  });

  // 4. When token exists, axios.get is called and Sidebar is rendered.
  test("renders Sidebar when token exists and profile is fetched", async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByTestId("sidebar")).toBeInTheDocument();
    });
  });

  // 5. Clicking "LogOut" displays the logout modal.
  test("displays logout modal when LogOut is clicked", async () => {
    render(<App />);
    await waitFor(() => {
      const logoutBtn = screen.getByText(/LogOut/i);
      fireEvent.click(logoutBtn);
    });
    const modalHeader = screen.getByText(/Confirm Logout/i);
    expect(modalHeader).toBeInTheDocument();
  });

  // 6. Confirming logout removes token and hides the Sidebar.
  // Modified to scope the "Logout" button search within the modal.
  test("confirming logout removes token and hides sidebar", async () => {
    render(<App />);
    await waitFor(() => {
      const logoutBtn = screen.getByText(/LogOut/i);
      fireEvent.click(logoutBtn);
    });
    // Scope search within the modal overlay to find the confirm button.
    const modalOverlay = screen
      .getByText(/Confirm Logout/i)
      .closest(".modal-overlay");
    const confirmBtn = within(modalOverlay).getByText(/^Logout$/i);
    fireEvent.click(confirmBtn);
    await waitFor(() => {
      expect(localStorage.getItem("token")).toBeNull();
      expect(screen.queryByTestId("sidebar")).toBeNull();
    });
  });

  // 7. Canceling logout hides the logout modal.
  test("cancel logout hides the logout modal", async () => {
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

  // 8. Clicking "Profile" sets currentPage to ProfilePage.
  // Modified to use getByRole for the button.
  test('switchPage sets currentPage to ProfilePage when "Profile" is clicked', async () => {
    render(<App />);
    await waitFor(() => {
      const profileBtn = screen.getByTestId(
        CONSTANTS.PAGES.PROFILE.TEXT + " Button"
      );
      fireEvent.click(profileBtn);
    });
    const profilePage = screen.getByTestId("profile-page");
    expect(profilePage).toBeInTheDocument();
  });

  // 9. Clicking "Search" sets currentPage to SearchPage.
  // Modified to use getByRole.
  test('switchPage sets currentPage to SearchPage when "Search" is clicked', async () => {
    render(<App />);
    await waitFor(() => {
      const searchBtn = screen.getByTestId(
        CONSTANTS.PAGES.SEARCH.TEXT + " Button"
      );
      fireEvent.click(searchBtn);
    });
    const searchPage = screen.getByTestId("search-page");
    expect(searchPage).toBeInTheDocument();
  });

  // 10. Clicking "Applications" sets currentPage to ApplicationPage.
  // Modified to use getByRole.
  test('switchPage sets currentPage to ApplicationPage when "Applications" is clicked', async () => {
    render(<App />);
    await waitFor(() => {
      const appBtn = screen.getByTestId(
        CONSTANTS.PAGES.APPLICATION.TEXT + " Button"
      );
      fireEvent.click(appBtn);
    });
    const applicationPage = screen.getByTestId("application-page");
    expect(applicationPage).toBeInTheDocument();
  });

  // 11. Clicking "Manage" sets currentPage to ManageResumePage.
  // Modified to use getByRole.
  test('switchPage sets currentPage to ManageResumePage when "Manage" is clicked', async () => {
    render(<App />);
    await waitFor(() => {
      const manageBtn = screen.getByTestId(
        CONSTANTS.PAGES.MANAGE_RESUME.TEXT + " Button"
      );
      fireEvent.click(manageBtn);
    });
    const managePage = screen.getByTestId("manage-resume-page");
    expect(managePage).toBeInTheDocument();
  });

  // 12. Clicking "Matches" sets currentPage to MatchesPage.
  // Modified to use getByRole.
  test('switchPage sets currentPage to MatchesPage when "Matches" is clicked', async () => {
    render(<App />);
    await waitFor(() => {
      const matchesBtn = screen.getByTestId(
        CONSTANTS.PAGES.MATCHES.TEXT + " Button"
      );
      fireEvent.click(matchesBtn);
    });
    const matchesPage = screen.getByTestId("matches-page");
    expect(matchesPage).toBeInTheDocument();
  });

  // 13. Renders main structure elements with correct classes.
  test("renders main structure elements with correct classes", async () => {
    render(<App />);
    expect(document.querySelector(".main")).toBeInTheDocument();
    expect(document.querySelector(".content")).toBeInTheDocument();
  });

  // 14. Logout modal is not rendered by default.
  test("logout modal is not rendered by default", () => {
    render(<App />);
    expect(document.querySelector(".modal-overlay")).toBeNull();
  });

  // 15. updateProfile updates userProfile and renders ProfilePage.
  test("updateProfile updates userProfile and renders ProfilePage", async () => {
    render(<App />);
    await waitFor(() => {
      const profilePage = screen.getByTestId("profile-page");
      expect(profilePage).toBeInTheDocument();
    });
  });

  // 16. When token exists, axios.get is called in componentDidMount.
  test("calls axios.get in componentDidMount when token exists", async () => {
    render(<App />);
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalled();
    });
  });

  // 17. sidebarHandler sets sidebar to true and renders Sidebar.
  test("sidebarHandler sets sidebar state to true and renders Sidebar", async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByTestId("sidebar")).toBeInTheDocument();
    });
  });

  // 18. Renders LoginPage inside the "content" div when sidebar is false.
  test("renders LoginPage inside content div when sidebar is false", () => {
    localStorage.removeItem("token");
    const { container } = render(<App />);
    const contentDiv = container.querySelector(".content");
    expect(contentDiv).toHaveTextContent("Login");
  });

  // 19. Logout modal displays correct content when active.
  test("renders logout modal with proper content when active", async () => {
    render(<App />);
    await waitFor(() => {
      fireEvent.click(screen.getByText(/LogOut/i));
    });
    expect(screen.getByText(/Confirm Logout/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Are you sure you want to logout/i)
    ).toBeInTheDocument();
  });

  // 20. Renders custom modal styling in a <style> tag.
  test("renders custom modal styling in a <style> tag", () => {
    render(<App />);
    const styleTag = document.querySelector("style");
    expect(styleTag).toBeInTheDocument();
  });
});

describe("Test Multiple Profiles", () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();

    profiles = [profile0, profile1, profile2];
    profileList = initialProfileList;
    defaultProfile = 0;

    localStorage.setItem("token", "dummy-token");
    localStorage.setItem("userId", "123");
    axios.get.mockImplementation(getImplementation);
    axios.post.mockImplementation(() =>
      Promise.resolve({
        data: {
          profileid: 3,
        },
      })
    );
  });

  // 21. Renders Profile dropdown in sidebar
  test("Renders Profile dropdown in sidebar", async () => {
    render(<App />);

    expect(await screen.findByText("Profile")).toBeInTheDocument();
  });

  // 22. Profile page renders current profile name
  test("Profile page renders current profile name", async () => {
    render(<App />);

    expect(await screen.findByText("Profile:")).toBeInTheDocument();
    expect(
      screen.getByDisplayValue(profileList[0].profileName)
    ).toBeInTheDocument();
  });

  // 23. Renders that the current profile is the default profile
  test("Renders that the current profile is the default profile", async () => {
    render(<App />);

    expect(await screen.findByTitle("Filled Star")).toBeInTheDocument();
  });

  // 24. Renders List of current profiles when profile dropdown is clicked
  test("Renders List of current profiles when profile dropdown is clicked", async () => {
    render(<App />);

    const profileList = await screen.findByText(/Profiles/i);
    profileList.click();

    expect(screen.getByText(profile0.profileName)).toBeInTheDocument();
    expect(screen.getByText(profile1.profileName)).toBeInTheDocument();
    expect(screen.getByText(profile2.profileName)).toBeInTheDocument();
  });

  // 25. When another profile is selected while on the profile page, that profile is displayed
  test("When another profile is selected while on the profile page, that profile is displayed", async () => {
    render(<App />);

    expect(
      await screen.findByDisplayValue(profileList[0].profileName)
    ).toBeInTheDocument();

    const profileListButton = await screen.findByText(/Profiles/i);
    profileListButton.click();

    let secondProfile = screen.getByText(profile1.profileName);
    secondProfile.click();

    expect(
      await screen.findByDisplayValue(profileList[1].profileName)
    ).toBeInTheDocument();
  });

  // 26. Add new profile button starts as disabled
  test("Add new profile button starts as disabled", async () => {
    render(<App />);

    const profileListButton = await screen.findByText(/Profiles/i);
    profileListButton.click();

    let addProfileButton = await screen.findByTestId("Add Profile Button");

    expect(addProfileButton).toBeInTheDocument();
    expect(addProfileButton).toBeDisabled();
  });

  // 27. When text is entered, the new profile butten is enabled
  test("When text is entered, the new profile butten is enabled", async () => {
    render(<App />);

    const profileListButton = await screen.findByText(/Profiles/i);
    profileListButton.click();

    let addProfileButton = await screen.findByTestId("Add Profile Button");
    expect(addProfileButton).toBeInTheDocument();

    let profileTextbox = screen.getByRole("textbox", {
      name: "newProfileName",
    });
    expect(profileTextbox).toBeInTheDocument();

    fireEvent.change(profileTextbox, { target: { value: "Testing Profile" } });
    expect(screen.getByDisplayValue("Testing Profile")).toBeInTheDocument();
    expect(addProfileButton).not.toBeDisabled();
  });

  // 28. When adding a new profile, it is added to the list of profile.
  test("When adding a new profile, it is added to the list of profile.", async () => {
    render(<App />);

    const profileListButton = await screen.findByText(/Profiles/i);
    profileListButton.click();

    let profileTextbox = screen.getByRole("textbox", {
      name: "newProfileName",
    });
    fireEvent.change(profileTextbox, { target: { value: "Testing Profile" } });

    let addProfileButton = await screen.findByTestId("Add Profile Button");
    addProfileButton.click();

    expect(screen.getByText(profile0.profileName)).toBeInTheDocument();
    expect(screen.getByText(profile1.profileName)).toBeInTheDocument();
    expect(screen.getByText(profile2.profileName)).toBeInTheDocument();
    expect(await screen.findByText("Testing Profile")).toBeInTheDocument();
  });

  // 29. Clicking on disabled add button doesn't send anything through
  test("Clicking on disabled add button doesn't send anything through", async () => {
    render(<App />);

    const profileListButton = await screen.findByText(/Profiles/i);
    profileListButton.click();

    let addProfileButton = await screen.findByTestId("Add Profile Button");

    expect(addProfileButton).toBeInTheDocument();
    expect(addProfileButton).toBeDisabled();

    addProfileButton.click();
    expect(axios.post).not.toHaveBeenCalled();
  });

  // 30. When having typed a value that already exists, add button is disabled
  test("When having typed a value that already exists, add button is disabled", async () => {
    render(<App />);

    const profileListButton = await screen.findByText(/Profiles/i);
    profileListButton.click();

    let addProfileButton = await screen.findByTestId("Add Profile Button");
    expect(addProfileButton).toBeInTheDocument();

    let profileTextbox = screen.getByRole("textbox", {
      name: "newProfileName",
    });
    fireEvent.change(profileTextbox, {
      target: { value: profileList[0].profileName },
    });

    expect(addProfileButton).toBeDisabled();
  });
});

describe("Test Cover Letter Feature", () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();

    profiles = [profile0, profile1, profile2];
    profileList = initialProfileList;
    defaultProfile = 0;

    localStorage.setItem("token", "dummy-token");
    localStorage.setItem("userId", "123");
    axios.get.mockImplementation(getImplementation);
    // axios.post.mockImplementation(() =>
    //   Promise.resolve({
    //     data: {
    //       profileid: 3,
    //     },
    //   })
    // );
  });

  test("", async () => {});
});
