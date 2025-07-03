import yaml

openweathermap_api_key = "8851f27a0b64cad1a226fb45ed3b6a3e"
brave_api_key = "BSA2468O5H1sMjZRxChKFvppvN710VU"

task_def = yaml.safe_load(f"""
# yaml-language-server: $schema=https://raw.githubusercontent.com/julep-ai/julep/refs/heads/dev/schemas/create_task_request.json
name: Foodie Tour Generator
description: A task that plans indoor/outdoor foodie tours based on city weather and local cuisine.
################################################# Input Schema #####################################################

input_schema:
  type: object
  properties:
    locations:
      type: array
      items:
        type: string
      description: List of cities to plan a foodie tour for.
##########################################################################################
################################## TOOLS ################################################
 
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
# Step 0: Fetch weather
- over: $ steps[0].input.locations
  map:
    tool: check_weather
    arguments:
      location: $ _
# Debug weather data
- evaluate:
    debug_weather: $ steps[0].output

# Step 1: Search iconic dishes
- over: $ steps[0].input.locations
  map:
    tool: search_dishes
    arguments:
      query: $ 'iconic dishes in ' + _


# Step 2: Search local restaurants
- over: $ steps[0].input.locations
  map:
    tool: search_restaurants
    arguments:
      query: $ 'best restaurants in ' + _


# Step 3: Zip all data for itinerary generation
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

# Step 4: Generate itinerary per city
- over: $ _['zipped']
  parallelism: 3
  map:
    prompt:
      - role: system
        content: >-
          $ f'''You are {{agent.name}}, an expert food and travel blogger...
          - Locations 
          - Weather
          - Dishes 
          - Local restaurants '''
      - role: user
        content: >-
          $ f'''Locations : "{{_[0]}}"
          Weather : "{{_[1]}}"
          Dishes : "{{_[2]}}"
          Local restaurants : "{{_[3]}}" '''
          
    unwrap: true

# Step 5: Combine all city itineraries
- evaluate:
    final_plan: |-
      $ '\\n---------------\\n'.join(activity for activity in _)
""")
