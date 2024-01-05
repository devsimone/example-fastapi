from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(
    prefix="/posts",  # This is now the basic of all of our endpoints paths
    tags=["Posts"]  # This is going to group all our post apis under Posts
)


@router.get("/", response_model=List[schemas.PostOut])
def get_post(db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user),
             # actually current_user shouldn't be int but user type
             limit: int = 10,
             skip: int = 0,
             search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")  # Here we just prepare our SQL Statement
    # posts = cursor.fetchall()  # Here we execute our SQL Statement

    # use the below code if you want to retrieve post only for the id of the actual logged user and not all of them
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # sqlalchemy by default implements inner joins
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search)).limit(limit).offset(skip)
        .all()
    )

    # we use list and map 'cause after v1.x when querying the db with two arguments in the .query method, sqlalchemy
    # returns a list of sqlalchemy.engine.row.Row objects.
    # Renamed RowProxy to .Row. .Row is no longer a "proxy" object in that it contains the final form of data within it,
    # and now acts mostly like a named tuple. Mapping-like functionality is moved to the .Row._mapping attribute, but
    # will remain available in SQLAlchemy 1.x ... "
    # we are not allowed to retrieve the jsonized data directly from the query anymore; the ._mapping method takes care
    # of building the dict structure with "Post" and "votes" keys, and using map does this for each .Row element in the
    # list; we then convert map to a list to be able to return it.
    return list(map(lambda x: x._mapping, posts))

# @app.post("/createposts")
# def create_posts(payload: dict = Body(...)):  # converts the response properties in a dictionary
#    print(payload)
#    return {"new_post": f"title: {payload['title']} content: {payload['content']}"}


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate,
                 db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    # # The %s is to pass the variable in a sanitised way (don't use the f-string as it's vulnerable)
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    #
    # new_post = cursor.fetchone()
    # conn.commit()  # This is going to push the changes to the DB

    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    # It's the same of doing the SQL command """ RETURNING * """, It's gonna retrieve the new post and store it back
    # into the variable new_post
    db.refresh(new_post)

    return new_post


# This endpoint must be placed before the one with "/posts/{id}"
# as otherwise it'll try to convert "/latest" into an {id}, the order matters
# @router.get("/posts/latest")
# def get_latest_post():
#     post = my_post[len(my_post) - 1]
#     return {"detail": post}


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # # id to be inserted into the DB must be a string
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .all()
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id : {id} was not found")

    # use the below code if you want to retrieve post only for the id of the actual logged user and not all of them
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action")

    return list(map(lambda x: x._mapping, post))[0]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    # we define a query
    post_query = db.query(models.Post).filter(models.Post.id == id)

    # we execute the query
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id : {id} doesn't exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action")

    # we grab the original query, and then we're gonna append a delete command that we delete it
    post_query.delete(synchronize_session=False)
    # and in the end we commit the delete command to the DB
    db.commit()

    # When you delete something, just return 204 and don't send any data back
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int,
                updated_post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))
    #
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id : {id} doesn't exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()
