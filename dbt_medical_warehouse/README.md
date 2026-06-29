Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
## Task 4: Business Intelligence & Dashboard Integration

### 1. Data Warehouse Connection
* Established a native connection between Power BI Desktop and the local PostgreSQL analytical warehouse layer (`dbt` transformed schema).

### 2. Star Schema Data Modeling
* Designed and verified a dimensional star schema within Power BI.
* Configured robust One-to-Many ($1 \rightarrow *$) relationship chains branching from the master dimension table into both analytical fact tables using `channel_key`:
  * `main dim_channels` $\rightarrow$ `main fct_image_detections`
  * `main dim_channels` $\rightarrow$ `main fct_medical_alerts`

### 3. Interactive Visualization Development
* **YOLO Computer Vision Telemetry:** Built a targeted category bar chart utilizing an explicit custom DAX measure (`Total_Detections = COUNT('main fct_image_detections'[image_detection_key])`) to accurately parse and track the frequency distribution of extracted objects (e.g., bottles, laptops, books).
* **Commercial Activity Analysis:** Formatted an optimized donut chart mapping the exact operational ratio between organic healthcare channel alerts and paid commercial advertisements (`is_commercial_ad`).
* **Global Control Filters:** Implemented an interactive master `channel_name` slicer, enabling cross-filtering across the entire report canvas simultaneously (e.g., dynamically isolating metrics for channels like `TikvahPharma`).
