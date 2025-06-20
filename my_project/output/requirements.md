Functional Requirements:

FR-001: Task Creation
Description: Users should be able to create tasks with various attributes including task name, task description, task category/project, due date, priority level, task assignee, and task status.
Acceptance Criteria: A user can create a task, fill out all necessary fields, and save the task successfully. The task should appear in the user's task list.
Priority: High
Source: User Story 1, Q&A 1

FR-002: Task Categorization
Description: Users should be able to categorize tasks into different projects. Within each project, tasks can be organized hierarchically and also tagged/labelled for additional flexibility.
Acceptance Criteria: A user can create a project, assign tasks to it, create a hierarchy of tasks, and assign labels/tags to tasks. The user can filter or sort tasks based on these categories.
Priority: High
Source: User Story 2, Q&A 2

FR-003: Task Status Update
Description: Users should be able to update the status of a task to reflect its current state. The system should support multiple status options including 'Not Started', 'In Progress', 'On Hold', 'Complete', and 'Blocked'.
Acceptance Criteria: A user can change the status of a task. The updated status is correctly reflected in the task list and any related views.
Priority: High
Source: User Story 3, Q&A 3

FR-004: Task Deletion
Description: Users should be able to delete tasks. The system should support both soft deletion (archiving) and hard deletion (permanent removal), with appropriate user permissions.
Acceptance Criteria: A user can delete a task. The task is removed from the task list and either archived or permanently deleted based on user permissions.
Priority: Medium
Source: User Story 4

FR-005: Task Management for Administrators
Description: Administrators should be able to view and manage all tasks. They should have access to detailed task information and the ability to edit tasks as necessary.
Acceptance Criteria: An administrator can view a list of all tasks, view detailed information for each task, and make edits to tasks. Changes made by the administrator are correctly reflected in the system.
Priority: High
Source: User Story 5

Non-Functional Requirements:

NFR-001: System Performance
Description: The task management system should be fast and responsive, with a maximum response time of 2 seconds for key actions such as task creation, task status update, and task deletion.
Acceptance Criteria: System performance is tested under normal and peak loads. Key actions are completed within the target response time.
Priority: High
Source: Non-Functional Requirement 6

NFR-002: System Availability
Description: The system should be reliable and available 24/7, with a target uptime of 99.9%.
Acceptance Criteria: System availability is monitored and reported. The system achieves the target uptime over a specified period.
Priority: High
Source: Non-Functional Requirement 7

NFR-003: System Usability
Description: The system should have an intuitive interface that is easy to use and navigate. The system should achieve a System Usability Scale (SUS) score of 70 or above.
Acceptance Criteria: Usability is tested with a group of target users. The system achieves the target SUS score.
Priority: High
Source: Non-Functional Requirement 8

System Constraints and Assumptions:

- The system will be a web-based application, accessible via modern web browsers.
- The system will support multiple user roles with different permissions (e.g., primary users, administrators).
- The system will be used by individuals or teams for managing tasks related to various projects.

Data Requirements:

- Key data entities include Users, Tasks, and Projects.
- Tasks have various attributes including Task Name, Task Description, Task Category/Project, Due Date, Priority Level, Task Assignee, and Task Status.
- Data relationships include: Users can create multiple Tasks, Tasks can be assigned to specific Projects, Tasks can be assigned to specific Users.