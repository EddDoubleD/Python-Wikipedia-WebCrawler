def continue_crawl(search_history,target_url):
    if search_history[-1]==target_url:
        print("The target url has been reached")
        return False
    elif len(search_history)>25:
        print("Target no reached in threshold value :25")
        return False
    elif search_history[-1] in search_history[:-1]:
        print("The program is going on a cycle")
        return False
    else:
        return True
    