from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE OR REPLACE FUNCTION public.update_pipe_fitting_by_module()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            NEW.typical_location := CASE
                WHEN NEW.module_id = 1 THEN 'main_pipe'
                WHEN NEW.module_id = 5 THEN 'nozzle'
                WHEN NEW.module_id = 8 THEN 'micro_sprinkler'
                WHEN NEW.module_id = 9 THEN 'dripper'
                WHEN NEW.module_id = 6 THEN 'perforated_pipe'
                ELSE 'fitting'
            END;

            NEW.is_terminal := CASE
                WHEN NEW.module_id IN (5, 6, 8, 9) THEN TRUE
                ELSE FALSE
            END;

            RETURN NEW;
        END;
        $function$;

        DROP TRIGGER IF EXISTS trg_set_pipe_fitting_by_module ON public.pipe_fittings;

        CREATE TRIGGER trg_set_pipe_fitting_by_module
            BEFORE INSERT OR UPDATE ON public.pipe_fittings
            FOR EACH ROW
            EXECUTE FUNCTION public.update_pipe_fitting_by_module();

        UPDATE public.pipe_fittings SET module_id = module_id WHERE typical_location IS NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TRIGGER IF EXISTS trg_set_pipe_fitting_by_module ON public.pipe_fittings;
        DROP FUNCTION IF EXISTS public.update_pipe_fitting_by_module();"""
