-- A view comprising of content meta and content versions, and
-- which only contains the last published version
create or replace view content as
    select
        a.id,
        a.version,
        a.modifier_id,
        a.modified_date,
        a.title,
        a.content,
        a.state,
        b.author_id,
        b.create_date,
        b.like_count,
        b.read_count,
        b.comment_count,
        b.category,
        b.refers_to
    from
        content_meta b,
        content_versions a
    where
        a.id=b.id
        and
        (a.id, a.version) in (
            select
                content_versions.id,
                max(content_versions.version)
            from content_versions
            where state=50 group by content_versions.id);

CREATE TRIGGER tr_on_content_update
    BEFORE UPDATE ON content
    EXECUTE PROCEDURE fn_on_content_update();
