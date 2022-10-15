"""fix-typo

Revision ID: 95a761d0bc91
Revises: 274098d8e256
Create Date: 2022-10-15 12:17:09.387789

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '95a761d0bc91'
down_revision = '274098d8e256'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('DROP TRIGGER trigger_create_history_entry_for_setting ON setting;')
    op.execute('DROP FUNCTION create_history_entry_for_setting;')

    op.alter_column('setting', column_name='disable', new_column_name='disabled')
    op.alter_column('setting_history', column_name='disable', new_column_name='disabled')

    op.execute(upgrade_trigger_create_history_entry_for_setting)


def downgrade() -> None:
    op.execute('DROP TRIGGER trigger_create_history_entry_for_setting ON setting;')
    op.execute('DROP FUNCTION create_history_entry_for_setting;')

    op.alter_column('setting', column_name='disabled', new_column_name='disable')
    op.alter_column('setting_history', column_name='disabled', new_column_name='disable')

    op.execute(downgrade_trigger_create_history_entry_for_setting)


upgrade_trigger_create_history_entry_for_setting = """
    CREATE FUNCTION create_history_entry_for_setting() RETURNS trigger AS
    $$
    BEGIN
        IF TG_OP = 'UPDATE' THEN
            INSERT INTO setting_history (
                     name,
                     value,
                     value_type,
                     disabled,
                     service_name,
                     created_by_db_user,
                     updated_at
            )
            VALUES (
                    OLD.name,
                    OLD.value,
                    OLD.value_type,
                    OLD.disabled,
                    OLD.service_name,
                    OLD.created_by_db_user,
                    OLD.updated_at
            );
        ELSIF TG_OP = 'DELETE' THEN
            INSERT INTO setting_history (
                     name,
                     value,
                     value_type,
                     disabled,
                     service_name,
                     created_by_db_user,
                     updated_at,
                     is_deleted,
                     deleted_by_db_user
            )
            VALUES (
                    OLD.name,
                    OLD.value,
                    OLD.value_type,
                    OLD.disabled,
                    OLD.service_name,
                    OLD.created_by_db_user,
                    OLD.updated_at,
                    true,
                    session_user
            );
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE 'plpgsql' SECURITY DEFINER;

    CREATE TRIGGER trigger_create_history_entry_for_setting
        AFTER INSERT OR UPDATE OR DELETE
        ON setting
        FOR EACH ROW
    EXECUTE PROCEDURE create_history_entry_for_setting();
"""  # noqa=E501

downgrade_trigger_create_history_entry_for_setting = """
    CREATE FUNCTION create_history_entry_for_setting() RETURNS trigger AS
    $$
    BEGIN
        IF TG_OP = 'UPDATE' THEN
            INSERT INTO setting_history (
                     name,
                     value,
                     value_type,
                     disable,
                     service_name,
                     created_by_db_user,
                     updated_at
            )
            VALUES (
                    OLD.name,
                    OLD.value,
                    OLD.value_type,
                    OLD.disable,
                    OLD.service_name,
                    OLD.created_by_db_user,
                    OLD.updated_at
            );
        ELSIF TG_OP = 'DELETE' THEN
            INSERT INTO setting_history (
                     name,
                     value,
                     value_type,
                     disable,
                     service_name,
                     created_by_db_user,
                     updated_at,
                     is_deleted,
                     deleted_by_db_user
            )
            VALUES (
                    OLD.name,
                    OLD.value,
                    OLD.value_type,
                    OLD.disable,
                    OLD.service_name,
                    OLD.created_by_db_user,
                    OLD.updated_at,
                    true,
                    session_user
            );
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE 'plpgsql' SECURITY DEFINER;

    CREATE TRIGGER trigger_create_history_entry_for_setting
        AFTER INSERT OR UPDATE OR DELETE
        ON setting
        FOR EACH ROW
    EXECUTE PROCEDURE create_history_entry_for_setting();
"""  # noqa=E501
