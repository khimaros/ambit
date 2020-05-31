# THREADING

Start a read thread reading in a loop with high timeout.

All processing in the read thread happens synchronously.

Start a write thread, polling for new items to write.

two additional queues are used for managing `screen_string` and `led` writes.
