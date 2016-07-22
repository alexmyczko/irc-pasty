import os

def savePost(directory, id, content, title):
    try:
        file = open(os.path.join(directory, id + '-' + title), 'w')
        file.write(content)
        file.close()
        return False
    except:
        print('write error')
        return True

def getPost(id):
    try:
        posts = os.listdir('posts')
        title = None

        for post in posts:
            if id in post:
                title = post.rpartition('-')[2]

        if title == None:
            return None

        file = open(os.path.join('posts', id + '-' + title), 'r')
        content = file.read()
        file.close()
        return { 'content' : content, 'title' : title }
    except:
        return False