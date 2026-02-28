<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style lang="scss">
	@import '@/uni_modules/uni-scss/index.scss';
	@import '@/static/customicons.css';
	
	page {
		background-color: #f5f5f5;
		color: #333;
	}
</style>