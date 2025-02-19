<script>
    import { adminStatus } from '../stores.js';

    let logo = "/static/HKN-Logo-New-Blue.png";
    let onLogOut = () => {
        sessionStorage.removeItem('adminStatus');
        
    }
</script>
