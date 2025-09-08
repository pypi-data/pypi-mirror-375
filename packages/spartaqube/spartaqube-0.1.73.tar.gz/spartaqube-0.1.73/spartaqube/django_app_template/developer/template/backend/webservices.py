def sparta_ce33acbe9b(service: str, post_data: dict, user=None) ->dict:
    """
    Implement your webservices here
    1. Use the service name to differentiate the webservices
    2. User's data are sent within the dictionary post_data
    3. The user variable can be used to differentiate the user who run the query
    """
    print(f'Service: {service}')
    if service == 'fetch_code_snippet':
        from examples.examples_snippet import sparta_a7f05d32c5
        return sparta_a7f05d32c5(post_data)
    elif service == 'example_simple_api':
        from examples.api_driven.simple_api_call import sparta_a7f05d32c5
        return sparta_a7f05d32c5(post_data)
    elif service == 'example_plot_yahoo':
        from examples.api_driven.plot_yahoo import sparta_a7f05d32c5
        return sparta_a7f05d32c5(post_data)
    return {'res': 1}

#END OF QUBE
