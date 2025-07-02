import yaml

openweathermap_api_key = "a27281781a28ee99f89845db78152ef5"
brave_api_key = "BSA2468O5H1sMjZRxChKFvppvN710VU"

task_def = yaml.safe_load(f"""

# yaml-language-server: $schema=https://raw.githubusercontent.com/julep-ai/julep/refs/heads/dev/schemas/create_task_request.json
name: Foodie Tour Generator
description: A task that plans indoor/outdoor foodie tours based on city weather and iconic local dishes.

input_schema:
  type: object
  properties:
    locations:
      type: array
      items:
        type: string
      description: List of cities to plan a foodie tour for Planning things .

tools:
- name: check_weather
  type: integration
  integration:
    provider: weather
    setup:
      openweathermap_api_key: {openweathermap_api_key}

- name: search_dishes
  type: integration
  integration:
    provider: brave
    setup:
      brave_api_key: {brave_api_key}

- name: search_restaurants
  type: integration
  integration:
    provider: brave
    setup:
      brave_api_key: {brave_api_key}

main:
# Step 0: Get weather for each location
- over: $ steps[0].input.locations
  map:
    tool: check_weather
    arguments:
      location: $ _

# Step 1: Get iconic dishes per location
- over: $ steps[0].input.locations
  map:
    tool: search_dishes
    arguments:
      query: $ 'iconic dishes in ' + _

# Step 2: Get local restaurants per location
- over: $ steps[0].input.locations
  map:
    tool: search_restaurants
    arguments:
      query: $ 'best restaurants in ' + _

# Step 3: Zip locations, weather, dishes, and restaurants
- evaluate:
    zipped: |-
      $ list(
        zip(
          steps[0].input.locations,
          steps[0].output,
          steps[1].output,
          steps[2].output
        )
      )

# Step 4: Generate foodie itinerary per city
- over: $ _['zipped']
  parallelism: 3
  map:
    prompt:
    - role: system
      content: >-
        $ f'''You are {{agent.name}}. an expert travel and food blogger. Given weather, dishes, and restaurants for a city, create an itinerary with breakfast, lunch, and dinner. Recommend indoor/outdoor dining based on weather. Use the following info:
        - Location
        - Current Weather
        - Dishes
        - Restaurants'''

    - role: user
      content: >-
        $ f'''City: "{{_[0]}}"
        Weather: "{{_[1]}}"
        Iconic Dishes: "{{_[2]}}"
        Local Restaurants: "{{_[3]}}"'''
    unwrap: true

# Step 5: Join all itineraries into a final result
- evaluate:
    final_plan: |-
      $ '\\n---------------\\n'.join(activity for activity in _)

""")
