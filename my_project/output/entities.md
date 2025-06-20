1. ACTORS

   - Name: User
     - Type: Actor
     - Description: The primary user of the system who creates, categorizes, updates, and deletes tasks.
     - Attributes: User ID, Username, Password, Task List, Role
     - Role: Interacts with the system to manage tasks and projects.
     
   - Name: Administrator
     - Type: Actor
     - Description: Special type of user who has additional permissions to view and manage all tasks in the system.
     - Attributes: User ID, Username, Password, Task List, Role
     - Role: Oversees and manages all tasks and users in the system.

2. DATA OBJECTS

   - Name: Task
     - Type: Data Object
     - Description: Represents a task created by users, which can be categorized into projects, updated, and deleted.
     - Attributes: Task ID, Task Name, Task Description, Task Category/Project, Due Date, Priority Level, Task Assignee, Task Status
     - Constraints: All attributes are required. Task status must be one of 'Not Started', 'In Progress', 'On Hold', 'Complete', 'Blocked'.
  
   - Name: Project
     - Type: Data Object
     - Description: Represents a project under which tasks can be categorized.
     - Attributes: Project ID, Project Name, Task List
     - Constraints: Both project ID and project name are required. Tasks in the task list must exist in the system.

3. PROCESSES

   - Name: Task Creation
     - Type: Process
     - Description: Allows users to create tasks.
     - Inputs: Task attributes
     - Outputs: New task
     - Triggers: User action

   - Name: Task Categorization
     - Type: Process
     - Description: Allows users to categorize tasks into projects.
     - Inputs: Task, Project
     - Outputs: Categorized task
     - Triggers: User action

   - Name: Task Status Update
     - Type: Process
     - Description: Allows users to update the status of tasks.
     - Inputs: Task, New status
     - Outputs: Updated task
     - Triggers: User action

   - Name: Task Deletion
     - Type: Process
     - Description: Allows users to delete tasks.
     - Inputs: Task
     - Outputs: Deletion confirmation
     - Triggers: User action

   - Name: Task Management for Administrators
     - Type: Process
     - Description: Allows administrators to view and edit all tasks.
     - Inputs: Task, Administrator actions
     - Outputs: Updated task
     - Triggers: Administrator action

4. SYSTEM COMPONENTS

   - Name: Task Management System
     - Type: System Component
     - Description: The main system that provides task management functionality.
     - Responsibilities: Manages tasks and projects, supports user interactions, maintains system performance and availability
     - Interfaces: User interface, Administrator interface

   - Name: User Interface
     - Type: System Component
     - Description: The interface through which users interact with the system.
     - Responsibilities: Displaying tasks and projects, receiving user inputs, providing feedback to users
     - Interfaces: Task Management System

   - Name: Administrator Interface
     - Type: System Component
     - Description: The interface through which administrators interact with the system.
     - Responsibilities: Displaying all tasks, receiving administrator inputs, providing feedback to administrators
     - Interfaces: Task Management System